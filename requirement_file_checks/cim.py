#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import os.path
from typing import List
from xml.etree import cElementTree as ET

from base_checker import BaseChecker


class CimChecker(BaseChecker):
    def __init__(self, filenames: List[str]):
        super().__init__("cim_checker", filenames)
        self._models_dir = os.path.join(
            os.path.dirname(__file__),
            "../",
            "CIM_Models",
        )

    def _check(self, filename: str):
        counter = 0
        # Parsing xml file
        root = fetch_root_xml(filename)
        if root is None:
            print("----------------------------------------------")
            print("ERROR parsing xml file" + filename)
            return
        for cim in root.iter("event"):
            fields_xml = fetch_xml_fields(cim)
            model_list = fetch_models(cim)
            event = fetch_event_xml(cim)
            jsondir = _fetch_cim_version_event(cim, self._models_dir)
            if jsondir is None:
                print("No matching CIM version found")
                continue
            counter += 1
            if len(model_list) > 0:
                for model in model_list:
                    model, dataset, subdataset = fetch_model_name(model)
                    if dataset:
                        dataset = dataset.replace(" ", "_")
                    if subdataset:
                        subdataset = subdataset.replace(" ", "_")
                    cim_file = model + ".json"
                    fname = os.path.join(self._models_dir + jsondir, cim_file)
                    try:
                        with open(fname) as f:
                            dict_model = json.load(f)
                    except OSError:
                        print_error_msg(
                            filename,
                            event,
                            model,
                            "ERROR: No CIM model with this name, Please check the format- model:dataset and models at deps/CIM_Models/"
                            + str(jsondir),
                        )
                        continue
                    # Dataset valid check
                    if dataset:
                        dataset_valid_flag = check_valid_dataset(
                            dict_model["objects"], dataset
                        )
                        if not dataset_valid_flag:
                            error_str = (
                                "ERROR: No matching dataset present in "
                                + str(cim_file)
                                + " at "
                                + str(jsondir)
                            )
                            print_error_msg(filename, event, model, error_str, dataset)
                            continue
                    # Require dataset for Endpoint and Splunk-audit
                    if model == "Endpoint" and model == "Splunk_Audit":
                        if not dataset:
                            print_error_msg(
                                filename,
                                event,
                                model,
                                "ERROR: dataset required for these models",
                            )
                            continue
                    # Fetch baseEvent recommended fields
                    dataset_recommended = []
                    recommended_for_all = fetch_base_event_recommended(
                        dict_model["objects"]
                    )
                    if dataset:
                        try:
                            dataset_recommended = fetch_json_fields_with_dataset(
                                dict_model["objects"], dataset, subdataset, model
                            )
                        except Exception:
                            continue
                    field_json = recommended_for_all + dataset_recommended
                    missing_fields = match_recommended_fields(field_json, fields_xml)
                    if missing_fields:
                        print("----------------------------------------------")
                        print("FILENAME : " + str(filename))
                        print("CIM VERSION :" + str(jsondir))
                        print("EVENT : " + str(event))
                        print("MODEL : " + str(model))
                        if dataset:
                            print("DATASET : " + str(dataset))
                        if subdataset:
                            print("SUBDATASET : " + str(subdataset))
                        print(
                            "CIM BASE EVENT RECOMMENDED : "
                            + (", ".join(recommended_for_all))
                        )
                        if dataset or dataset_recommended:
                            print(
                                "CIM DATASET RECOMMENDED : "
                                + (", ".join(dataset_recommended))
                            )
                        print(
                            "REQUIREMENT FILE RECOMMENDED : " + (", ".join(fields_xml))
                        )
                        print(
                            "MISSING CIM RECOMMENDED IN REQUIREMENT FILE : "
                            + (",".join(set(missing_fields)))
                        )


# function to return generator object for given field
def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            yield from find(key, v)
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    yield from find(key, d)


# extracting lists based on the key given
def extract_values(obj, key):
    arr = []

    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


# to find if xml is missing recommended fields
def match_recommended_fields(field_json, field_xml):
    fields = []
    for i in field_json:
        if i not in field_xml:
            fields += [i]
    return fields


# fetch json fields when dataset is given
def fetch_json_fields_with_dataset(dict_model, dataset, subdataset, model_name):
    field_json = []
    objectName = None
    dataset_match_flag = False
    for i in range(len(dict_model)):
        objectName = extract_values(dict_model[i], "objectName")
        if (
            (dataset in objectName)
            or (model_name in objectName)
            or (subdataset in objectName)
        ):
            listVar = list(find("outputFields", dict_model[i]))
            listVar2 = list(find("fields", dict_model[i]))
            dataset_match_flag = True
            # for fields with recommended = true
            for k in listVar2:
                for l in k:
                    reco_list2 = extract_values(l, "recommended")
                    if True in reco_list2:
                        field_json += extract_values(l, "fieldName")
            # to extract output_fields where recommended = true
            for j in range(len(listVar)):
                reco_list = extract_values(listVar[j], "recommended")
                if True in reco_list:
                    field_json += extract_values(listVar[j], "fieldName")
    # Error scenario when wrong dataset name given by xml
    if not dataset_match_flag:
        print("No matching dataset in file")
        raise ValueError("a")
    return field_json


def fetch_xml_fields(root):
    field_xml = []
    for fields in root.iter("field"):
        if fields.get("name"):
            string = fields.get("name")
            field_xml += [string]
        elif fields.text:
            string = fields.text
            field_xml += [string]
    return field_xml


def fetch_models(root):
    model_list = []
    for model in root.iter("model"):
        model_list.append(str(model.text))
    return model_list


# fetches root
def fetch_root_xml(file_name):
    root = None
    try:
        tree = ET.parse(file_name)
        root = tree.getroot()
    except:
        pass
    return root


# fetches event in event
def fetch_event_xml(root):
    for raw in root.iter("raw"):
        event = raw.text.encode("utf-8")
        event = event.lstrip()
        event = event.rstrip()
    return event


def fetch_base_event_recommended(dict_model):
    recommended_for_all = []
    for i in range(len(dict_model)):
        parentName = extract_values(dict_model[i], "parentName")
        if "BaseEvent" in parentName:
            listVar = list(find("outputFields", dict_model[i]))
            listVar2 = list(find("fields", dict_model[i]))
            # for fields with recommended = true
            for k in listVar2:
                for l in k:
                    reco_list2 = extract_values(l, "recommended")
                    if True in reco_list2:
                        recommended_for_all += extract_values(l, "fieldName")
            # to extract output_fields where recommended = true
            for j in range(len(listVar)):
                reco_list = extract_values(listVar[j], "recommended")
                if True in reco_list:
                    recommended_for_all += extract_values(listVar[j], "fieldName")

    return recommended_for_all


def check_valid_dataset(dict_model, dataset):
    datset_valid_flag = False
    for i in range(len(dict_model)):
        objectName = extract_values(dict_model[i], "objectName")
        if dataset in objectName:
            datset_valid_flag = True
    return datset_valid_flag


def print_error_msg(file_name, event, model, msg_str, dataset=""):
    print("----------------------------------------------")
    print("FILENAME : " + str(file_name))
    print("EVENT : " + str(event))
    print("MODEL : " + str(model))
    print("DATASET : " + str(dataset))
    print(msg_str)


# to extract model name from the xml file
def fetch_model_name(model_name):
    model_name = model_name.split(":", 2)
    if len(model_name) == 3:
        model = model_name[0]
        dataset = model_name[1]
        subdataset = model_name[2]
    elif len(model_name) == 2:
        model = model_name[0]
        dataset = model_name[1]
        subdataset = ""
    else:
        model = model_name[0]
        dataset = ""
        subdataset = ""
    if model:
        model = model.replace(" ", "_")
    return model, dataset, subdataset


def _fetch_latest_cim_ver(jsonpath):
    cim_model_dir = list()
    for root, dirs, files in os.walk(jsonpath, topdown=False):
        for name in dirs:
            cim_model_dir.append(os.path.join(name))
    cim_model_dir.sort(reverse=True)
    return cim_model_dir[0]


def _find_cim_dir(cim_version, jsonpath):
    cim_model_dir = list()
    for root, dirs, files in os.walk(jsonpath, topdown=False):
        for name in dirs:
            cim_model_dir.append(name)
    if cim_version in cim_model_dir:
        return cim_version
    else:
        matching_cim_versions = list()
        event_cim_version = cim_version.split(".")
        for elem in cim_model_dir:
            cim_ver_dir = elem.split(".")
            if (
                event_cim_version[0] == cim_ver_dir[0]
                and event_cim_version[1] == cim_ver_dir[1]
            ):
                matching_cim_versions.append(os.path.join(elem))
        if not matching_cim_versions:
            return None
        matching_cim_versions.sort(reverse=True)
        return matching_cim_versions[0]


def _fetch_cim_version_event(event, jsonpath):
    for cim_tag in event.iter("cim"):
        cim_version = cim_tag.get("version")
        if cim_version:
            cim_dir = _find_cim_dir(cim_version, jsonpath)
        else:
            # if CIM version not mentioned fetch the latest
            cim_dir = _fetch_latest_cim_ver(jsonpath)
    return cim_dir

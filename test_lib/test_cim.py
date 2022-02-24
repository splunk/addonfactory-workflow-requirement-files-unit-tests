# Test to check if XML contains all cim recommended fields based on the model name of the event
# Usage- test_cim.py -i <input log folder to test>
import getopt
import json
import logging
import os.path
import sys
from xml.etree import cElementTree as ET

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
output_file_handler = logging.FileHandler("test_cim_output.txt", mode="w")
stdout_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(output_file_handler)
logger.addHandler(stdout_handler)

HELP_STR = "test_cim.py -i <input log folder to test>"
JENKINS_STATUS = True
test_cim_output = open("test_cim_output.txt", "w")


def input_error():
    print(HELP_STR)
    exit(1)


# fetch json fields when dataset is not given
def fetch_json_fields(dict_model):
    listVar = list(find("outputFields", dict_model))
    field_json = []
    for i in range(len(listVar)):
        reco_list = extract_values(listVar[i], "recommended")
        if True in reco_list:
            field_json += extract_values(listVar[i], "fieldName")
    return field_json


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
        logging.error("No matching dataset in file")
        raise ValueError("a")
    return field_json


# fetch fields from the xml file. Return
def fetch_xml_fields(root):
    field_xml = []
    # tree = ET.parse(file_name)
    # root = tree.getroot()
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
    logger.error("----------------------------------------------")
    logger.error("FILENAME : " + str(file_name))
    logger.error("EVENT : " + str(event))
    logger.error("MODEL : " + str(model))
    logger.error("DATASET : " + str(dataset))
    logger.error(msg_str)


def cim_matching(file_name, jsonpath):
    counter = 0
    global JENKINS_STATUS
    # Parsing xml file
    root = fetch_root_xml(file_name)
    if root is None:
        JENKINS_STATUS = False
        logger.error("----------------------------------------------")
        logger.error("ERROR parsing xml file" + file_name)
        return
    for cim in root.iter("event"):
        fields_xml = fetch_xml_fields(cim)
        model_list = fetch_models(cim)
        event = fetch_event_xml(cim)
        jsondir = fetch_cim_version_event(cim, jsonpath)
        if jsondir is None:
            logger.error("No matching CIM version found")
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
                fname = os.path.join(jsonpath + jsondir, cim_file)
                try:
                    with open(fname) as f:
                        dict_model = json.load(f)
                except OSError:
                    JENKINS_STATUS = False
                    print_error_msg(
                        file_name,
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
                        print_error_msg(file_name, event, model, error_str, dataset)
                        continue
                # Require dataset for Endpoint and Splunk-audit
                if model == "Endpoint" and model == "Splunk_Audit":
                    if not dataset:
                        print_error_msg(
                            file_name,
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
                    JENKINS_STATUS = False
                    logger.error("----------------------------------------------")
                    logger.error("FILENAME : " + str(file_name))
                    logger.error("CIM VERSION :" + str(jsondir))
                    logger.error("EVENT : " + str(event))
                    logger.error("MODEL : " + str(model))
                    if dataset:
                        logger.error("DATASET : " + str(dataset))
                    if subdataset:
                        logger.error("SUBDATASET : " + str(subdataset))
                    logger.error(
                        "CIM BASE EVENT RECOMMENDED : "
                        + (", ".join(recommended_for_all))
                    )
                    if dataset or dataset_recommended:
                        logger.error(
                            "CIM DATASET RECOMMENDED : "
                            + (", ".join(dataset_recommended))
                        )
                    logger.error(
                        "REQUIREMENT FILE RECOMMENDED : " + (", ".join(fields_xml))
                    )
                    logger.error(
                        "MISSING CIM RECOMMENDED IN REQUIREMENT FILE : "
                        + (",".join(set(missing_fields)))
                    )


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
    return (model, dataset, subdataset)


def parse_args(argv):
    input_dir = None
    json_dir = None
    if len(argv) < 4:
        input_error()
    try:
        opts, _ = getopt.getopt(argv, "hi:j:")
    except getopt.GetoptError:
        input_error()
    for opt, arg in opts:
        if opt == "-h":
            input_error()
        elif opt in ("-i"):
            input_dir = arg
        elif opt in ("-j"):
            json_dir = arg
    return input_dir, json_dir


def fetch_latest_cim_ver(jsonpath):
    # this function will iterate over existing cim version and fetch the latest
    cim_model_dir = list()
    for root, dirs, files in os.walk(jsonpath, topdown=False):
        for name in dirs:
            cim_model_dir.append(os.path.join(name))
    cim_model_dir.sort(reverse=True)
    return cim_model_dir[0]


def find_cim_dir(cim_version, jsonpath):
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


def fetch_cim_version_event(event, jsonpath):
    for cim_tag in event.iter("cim"):
        cim_version = cim_tag.get("version")
        if cim_version:
            cim_dir = find_cim_dir(cim_version, jsonpath)
        else:
            # if CIM version not mentioned fetch the latest
            cim_dir = fetch_latest_cim_ver(jsonpath)
    return cim_dir


def main(argv):
    input_dir, json_dir = parse_args(argv)
    # run this for all files in the input folder given
    global JENKINS_STATUS
    if os.path.exists(input_dir):
        if os.path.isfile(input_dir):
            cim_matching(input_dir, str(json_dir))
        else:
            for subdir, _, files in os.walk(input_dir):
                for file in files:
                    filename = os.path.join(subdir, file)
                    if filename.endswith(".log") or filename.endswith(".xml"):
                        cim_matching(filename, str(json_dir))
    else:
        print("Invalid Input")
    if JENKINS_STATUS is False:
        exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

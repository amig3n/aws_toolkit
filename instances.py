import boto3
import yaml
import logging
import sys
import botocore
import re 
# from modifiers import *
import tabulate

with open('config.yaml') as config_file:
    logging.debug("Loading config.yaml")
    config = yaml.load(config_file, Loader=yaml.SafeLoader)
    logging.debug("Config file loaded")

def display_helptext():
    """Display help text"""
    print("Defined modifiers")
    # for modifier_object in MODIFIERS:
    #     print(f"{modifier_object.key} -> {modifier_object.helptext}")

def extract_tag(instance_data: dict, tag_key: str) -> str:
    """Extract tag from received aws output"""
    # Iterate over tags from instance
    for tag in instance_data['Tags']:
        if tag['Key'] == tag_key:
            return tag['Value']
        
def extract_nested_key(instance_data, key: str) -> str:
    """Extract nested key from received aws output"""

    return instance_data.get(key, None)
   
def extract_data(ec2_data: dict, data_keys: list[str]) -> list[dict]:
    """Extract data from received aws output"""

    record_set = {}

    # iterate over instances
    for instance in ec2_data['Reservations'][0]['Instances']:
        # handle data extraction

        for data_key in data_keys:
            # if data is tags, use proper function to handle those
            if re.match(data_key, "Tags."):

                tag_key = data_key.split('.')[1]
                record_set[data_key] = extract_tag(instance, tag_key) 
            elif re.match(data_key, "(.*\.)?.*"):
                # If data is nested, parse it and extract data from it
                logging.error(f"Nested data not implemented yet")
            else:
                record_set[data_key] = str(instance.get(data_key, None))

                
    return record_set


def apply_coloring(config: dict, records: list[dict]):
    """Apply coloring to the field, if they are mentioned in config"""
    colors_config = config['colors']

    for record in records:
        for field in record.keys():
            if field in colors_config:
                if record[field] in colors_config[field]['values'] :
                    record.update({field: f"{colors_config[field]['color']}{record[field]}\e[0m"})


def rewrite_titles(config: dict, records: list):
    """Rewrite titles according to config file"""
    pass

if __name__ == '__main__':
    MODIFIERS = compile_modifiers(config)
    
    # display help window
    if '--help' in sys.argv:
        display_helptext()
        exit(0)

    # prepare a list of fields to be extracted
    # if nothing is passed -> display default
    # if anything is passed -> verify existence and display it alongside the default
    # if something is passed that doesn't exist -> display error

    # NOTE use set to avoid duplicates
    fields_to_extract = set()

    # if no modifier is passed, use default group from config file
    if len(sys.argv) == 1:
        fields_to_extract = set(config.defaults)
    else:
        for modifier in sys.argv[1:]:
            if modifier in MODIFIERS:
                fields_to_extract = set(config.defaults if modifier['includeDefaults'] else [] + modifier['output'])
            else:
                logging.error(f"Modifier {modifier} is not defined")
                exit(1)

    # obtain info from AWS
    ec2 = boto3.client('ec2')
    try:
        instances_data = ec2.describe_instances()
    except botocore.exceptions.NoCredentialsError as e:
        logging.error(f"Error: {e}")
    
    records: list[dict] = extract_data(instances_data, fields_to_extract)

    # TODO rewrite titles
    if '--no-rewrite' not in sys.argv:
        rewrite_titles(records)

    # if --nocolor is passed, don't color output
    if '--nocolor' not in sys.argv:
        apply_coloring(records, fields_to_extract)

    # print output as table
    # prepare 
    headers = records[0].keys()
    values: list[list] = []
    
    for record in records:
        current_record: list[str] = []
        
        for key in headers:
            current_record.append(record.get(key, "<empty>"))
            logging.info(f"Record: {record}")

        values.append(current_record)
    
    logging.debug(f'Amount of transformed records: {len(records)}')
    
    print(tabulate(values, headers, tablefmt="simple"))
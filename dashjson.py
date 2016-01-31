#!/usr/bin/env python

import logging, argparse, json
from datadog import initialize, api

def loadjson(f):
    with open(f, 'r') as json_file:
        json_str = json_file.read()
        json_obj = json.loads(json_str)
        return json_obj

def authenticate(cred_json):
    initialize(**cred_json)

def import_json(dash_json, t):
    if t == "t":
        timeboard_json = dash_json['dash']
        title, description, graphs = timeboard_json['title'], timeboard_json['description'], timeboard_json['graphs']
        api.Timeboard.create(title=title, description=description, graphs=graphs)
    else:
        board_title, description, widgets = dash_json['board_title'], dash_json['description'], dash_json['widgets']
        api.Screenboard.create(board_title=board_title, description=description, widgets=widgets)

def export_json(dash_id, f, t):
    dash_json = api.Timeboard.get(dash_id) if t == "t" else api.Screenboard.get(dash_id)
    if dash_json:
        with open(f, 'w') as json_file:
            json.dump(dash_json, json_file, indent=4)

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=
    """
    A tool for importing datadog dashboards from json files and exporting them to json files.
    """
    )
    parser.add_argument("-c", "--credentials", required=True, help="the json file containing api_key and app_key as dictionary entries")
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument("-i", "--import_file", help="the json file to import dashboard definition from")
    mutex_group.add_argument("-e", "--export_file", help="the json file to export dashboard definition to")
    parser.add_argument("-d", "--dash_id", help="the id of the dashboard to be exported")
    parser.add_argument("-t", "--dash_type", choices=['t', 's'], default='t', help="the type of the dashboard to be imported or exported")
    args = parser.parse_args()

    if args.export_file and not args.dash_id:
       parser.print_help()
       sys.exit(1)

    authenticate(loadjson(args.credentials))

    if args.import_file:
        import_json(loadjson(args.import_file), args.dash_type)
    elif args.export_file and args.dash_id:
        export_json(args.dash_id, args.export_file, args.dash_type)

if __name__ == "__main__":
    main()
#!/usr/bin/env python

import sys, logging, argparse, json, os.path
from datadog import initialize, api

def load_json(f):
    with open(f, 'r') as json_file:
        json_str = json_file.read()
        json_obj = json.loads(json_str)
        return json_obj

def authenticate(cred_json):
    initialize(**cred_json)

def import_json(dash_json, t, update):
    if t == "t":
        timeboard_json = dash_json['dash']
        title, description, graphs = timeboard_json['title'], timeboard_json['description'], timeboard_json['graphs']
        if update:
            api.Timeboard.update(timeboard_json['id'], title=title, description=description, graphs=graphs)
        else:
            api.Timeboard.create(title=title, description=description, graphs=graphs)
    else:
        board_title, description, widgets = dash_json['board_title'], dash_json['description'], dash_json['widgets']
        if update:
           raise Exception('Update not supported for screenboards')
        else:
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
    A tool for exporting (or importing) datadog dashboards to (or from) json files.

    Examples

    - Export to json
    # python dashjson.py -e cool-graphs.json -d 12345

    - Import from json
    # python dashjson.py -i cool-graphs.json

    - Example content of the credentials file (your keys can be found at https://app.datadoghq.com/account/settings#api)
    # cat ~/.dashjson.json
    {
        "api_key": "abcdefg12345678",
        "app_key": "abcdefg987654321"
    }
    """, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-c", "--credentials", default=os.path.join(os.path.expanduser('~'), '.dashjson.json'), help="the json file containing api_key and app_key as dictionary entries, defaults to ~/.dashjson.json")
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument("-i", "--import_file", help="the json file to import dashboard definition from")
    mutex_group.add_argument("-e", "--export_file", help="the json file to export dashboard definition to")
    parser.add_argument("-d", "--dash_id", type=int, help="the id of the dashboard to be exported")
    parser.add_argument("-t", "--dash_type", choices=['t', 's'], default='t', help="the type of the dashboard (t for timeboard and s for screenboard) to be imported or exported")
    parser.add_argument("-u", "--update", dest='update', action='store_true', help="update an existing timeboard (used in combination with -i, not supported for screenboards))")
    parser.add_argument("-n", "--no-update", dest='update', action='store_false', help="create a new dashboard (used in combination with -i)")
    parser.set_defaults(update=True)
    args = parser.parse_args()

    if args.export_file and not args.dash_id:
       parser.print_help()
       sys.exit(1)

    authenticate(load_json(args.credentials))

    if args.import_file:
        import_json(load_json(args.import_file), args.dash_type, args.update)
    elif args.export_file and args.dash_id:
        export_json(args.dash_id, args.export_file, args.dash_type)

if __name__ == "__main__":
    main()

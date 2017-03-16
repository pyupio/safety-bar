[![safety](https://raw.githubusercontent.com/pyupio/safety/master/safety.png)](https://pyup.io/safety/)

## Usage:

```
git clone https://github.com/jayfk/menubar.git
cd menubar
pip install -r requirements.txt
python app.py
```

## Setting file:

The preference will be loaded from the `menubar` directory, and the settings is saved in JSON format:

```
<your menubar directory>/.pyupconfig
```

Example:

```json
{
    "startup": true,
    "api_key": "Your API Key",
    "paths": [
        {"path":"/Users/enix/Source/python/menubar","enable":false,"depth":1},    
        {"path":"/Users/enix/Source/python/menubar/test_files","enable":true,"depth":1}
    ]
}
```

Fields:

1. startup:  If true, then the app will be run with the system.
2. api_key:  The API key
3. paths dictionary:
    * path,  The directory path to be monitor
    * enable, A flag to indicate this path is active or not, if enable = false, the program will ignore this record, and dependencies will not be checked.
    * depth, Reseved for directory depth search, not used currently.

For example above, `menubar` directory is temporately disabled, so program will  ignore it, and `test_files` is active, so its dependencies will be check every hour.

## How to change the setting?

After running `app.py`, you can select `Preference` menu item from the menubar, and a preference window will be shown. So you can add/remove directoy as you want.

To temporately ignore the directory record, just uncheck the `Enable` column.

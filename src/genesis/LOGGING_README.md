# Logging Configuration

This directory now includes a comprehensive logging system that saves all console output to an `error.log` file while still displaying it in the console.

## Features

- **Dual Output**: All log messages appear both in the console and in the `logs/error.log` file
- **Timestamped**: All log entries include timestamps
- **Log Levels**: Supports different log levels (INFO, WARNING, ERROR, DEBUG)
- **Automatic Directory Creation**: Creates the `logs` directory if it doesn't exist
- **UTF-8 Encoding**: Ensures proper handling of special characters

## Files Modified

The following files have been updated to use the new logging system:

- `build_upload.py` - Replaced all `print()` statements with appropriate logging calls
- `bulk_download.py` - Replaced all `print()` statements with appropriate logging calls
- `export_to_csv.py` - Replaced all `print()` statements with appropriate logging calls
- `import_from_csv.py` - Replaced all `print()` statements with appropriate logging calls

## New Files

- `logging_config.py` - Contains the logging configuration setup
- `test_logging.py` - Test script to verify logging is working correctly
- `LOGGING_README.md` - This documentation file

## Usage

### Basic Usage

All scripts now automatically use the logging system. Simply run any script as before:

```bash
python build_upload.py
python bulk_download.py
python export_to_csv.py
python import_from_csv.py
```

### Testing the Logging

To test that logging is working correctly:

```bash
python test_logging.py
```

This will create test log entries and save them to `logs/error.log`.

### Log File Location

Log files are saved to:
```
logs/error.log
```

The `logs` directory is automatically created in the current working directory when any script runs.

## Log Levels

The logging system uses the following levels:

- **INFO**: General information messages (e.g., "Created ingredient: Apple")
- **WARNING**: Warning messages (e.g., "Unable to get nutrient information")
- **ERROR**: Error messages (e.g., "Request failed with status code 500")
- **DEBUG**: Debug messages (not shown by default)

## Configuration

The logging level is set to INFO by default. To change the logging level, modify the `level` parameter in `logging_config.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change this to DEBUG, INFO, WARNING, or ERROR
    # ... rest of configuration
)
```

## Benefits

1. **Persistence**: All console output is now saved to a file for later review
2. **Debugging**: Easier to troubleshoot issues by reviewing log files
3. **Audit Trail**: Complete record of all operations performed
4. **Consistency**: All scripts now use the same logging format
5. **Non-intrusive**: Console output remains the same, but is also saved to file 
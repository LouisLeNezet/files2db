import pandas as pd
import logging
from ..read_file.data_read import read_file
from ..ui.get_infos import get_file_path

def iterate_file(file):
    """Iterate through all files in the database

    All the files are read and concatenated into a single dataframe.
    The 'FileName' column is added to the resulting dataframe
    to indicate the source of each row of data.
    The metadata columns (starting with 'meta_') are also added to the dataframe.
    If a metadata column is not present in the file data, it is added with the value from the file info.

    Args:
        file (pd.DataFrame): Pandas dataframe containing the files to parse
            Each row should contain the following columns:
                - FileName: Name of the file to read
                - FilePath: Path to the file
                - Header: Header row number (1-based index)
                - LineStart: Start line number (1-based index)
                - LineEnd: End line number (1-based index)
                - ColStart: Start column letter (e.g., 'A')
                - ColEnd: End column letter (e.g., 'D')
                - SheetName: Name of the sheet to read (for Excel files)
                - Encoding: Encoding of the file (default is 'utf8')
                - Sep: Separator for CSV files (default is tab '\t')
            Metadata columns can also be included, prefixed with 'meta_'.
            They will be added to each row of the resulting dataframe.

    Returns:
        pd.DataFrame: Dataframe containing all the data from the files

    Raises:
        FileNotFoundError: If a file cannot be found or accessed
    """

    all_data = pd.DataFrame()
    metadata_columns = [
        col for col in file.columns if isinstance(col, str) and col.startswith("meta_")
    ]

    if file.empty:
        raise ValueError(
            "The input dataframe containing file information is empty. Please provide a valid dataframe."
        )

    for index in file.index:
        file_infos = file.loc[index].copy()
        file_name = file_infos["FileName"]
        file_path = get_file_path(file_infos["FilePath"])
        
        logging.info("Processing file: %s", file_name)

        # Set default for encoding and separator if not provided
        encoding=file_infos.get("Encoding", "utf8")
        sep=file_infos.get("Separator", "\t")

        if pd.isna(sep) or sep == "":
            sep = "\t"
        
        if pd.isna(encoding) or encoding == "":
            encoding = "utf8"

        # Read  file
        try:
            file_data = read_file(
                file_to_add_path=file_path,
                header=file_infos.get("Header"),
                line_start=file_infos.get("LineStart"),
                line_end=file_infos.get("LineEnd"),
                col_start=file_infos.get("ColStart"),
                col_end=file_infos.get("ColEnd"),
                sheet_name=file_infos.get("SheetName"),
                encoding=encoding,
                sep=sep,
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {file_path}") from e
        except Exception as e:
            raise e

        if "FileName" not in file_data.columns:
            file_data["FileName"] = file_name

        for col in metadata_columns:
            col_name = col.replace("meta_", "")
            if col_name not in file_data.columns:
                file_data[col_name] = file_infos[col]
            else:
                # If the column is already present, we can just skip it
                pass

        # Add file to merged data_frame
        all_data = pd.concat([all_data, file_data])
        all_data["RowIndex"] = all_data.index
        all_data.reset_index(drop=True, inplace=True)


    return all_data
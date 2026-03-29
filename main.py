
from thread_wise_processor_second import toiExtraction
from thread_wise_processor_first import thread_wise_process
from utility import SavefinalOutput,convert_json_toexcel
import os

def main():

    file_name="recent"
    MAIN_INPUT_FILE=f"input/{file_name}.xlsx"
    os.makedirs("analysis/mapping", exist_ok=True)
    os.makedirs("analysis/raw_output", exist_ok=True)
    os.makedirs("final_output",exist_ok=True)
    MAPPING_JSON_FILE=f"analysis/mapping/{file_name}_mapping_flow.json"
    MAPPING_EXL_FILE=f"analysis/mapping/{file_name}_mapping_flow.xlsx"
    MAIN_OUTPUT_FILE="analysis/raw_output/toi_results.json"
    FINAL_OUTPUT_FILE="final_output/final_result.xlsx"
    thread_wise_process(MAIN_INPUT_FILE,MAPPING_JSON_FILE)
    convert_json_toexcel(MAPPING_JSON_FILE,MAPPING_EXL_FILE) 
    EXTRACTED_DATAFRAME=toiExtraction(MAPPING_JSON_FILE,MAIN_OUTPUT_FILE)
    SavefinalOutput(EXTRACTED_DATAFRAME,MAIN_INPUT_FILE,FINAL_OUTPUT_FILE)



if __name__ == "__main__":
    main()
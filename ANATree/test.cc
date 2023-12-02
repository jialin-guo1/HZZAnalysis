#include <iostream>
#include <fstream>
#include <string>
#include "TString.h"
#include <typeinfo>

int test() {
    std::ifstream file("CrossSection.txt"); // Open the text file

    if (file.is_open()) { // Check if the file is successfully opened
        std::string line;
        TString targetString = "VBF_HToZZTo2L2Q_M2000_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8__v16_L1v1-v2_0.root";
        std::string delimiter = " ";

        while (std::getline(file, line)) {
            // Check if the target string is present in the current line
            if (line.find(targetString) != std::string::npos) {
                // Extract the associated value
                size_t pos = line.find(delimiter);
                std::string value = line.substr(pos + delimiter.length());
                std::cout << "Value: " << std::stof(value) << std::endl;
                break; // Stop further processing if the target is found
            }
        }

        file.close(); // Close the file
    } else {
        std::cout << "Failed to open the file." << std::endl;
    }

    return 0;
}


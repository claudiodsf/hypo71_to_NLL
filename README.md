# hypo71_to_NLL

`hypo71_to_NLL.py` is a script to convert [HYPO71] phase files to [NonLinLoc]
(NLL) phase files. 📄➡️📄

(c) 2024 - Claudio Satriano

## Requirements

- Python 3.x 🐍

## Installation

Clone the repository and navigate to the directory:

```sh
git clone https://github.com/claudiodsf/hypo71_to_NLL.git
cd hypo71_to_NLL
```

## Usage

Run the script with the following command:

```sh
python hypo71_to_NLL.py input_file output_file
```

Replace `input_file` with the path to your HYPO71 phase file and `output_file`
with the desired path for the NLL phase file.

If you don't specify an output file, the script will output the NLL phases to
the standard output.

Use the `-h` or `--help` flag to display the help message:

```sh
python hypo71_to_NLL.py -h
```

## Example

```sh
python hypo71_to_NLL.py example.hypo71 example.nll
```

## License

This project is licensed under the GNU General Public License v3.0 - see the
[LICENSE](LICENSE.txt) file for details. 📜

## Contact

For any questions or suggestions, please open an issue. 📨

[HYPO71]: https://doi.org/10.3133/ofr72224
[NonLinLoc]: https://github.com/ut-beg-texnet/NonLinLoc
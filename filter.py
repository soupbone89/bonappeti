# Define the input and output file paths
input_file = "unfiltered.txt"  # Change this to your file's name
output_file = "ports.txt"  # Name for the output file

# Open the input file and process the lines
with open(input_file, "r") as infile:
    lines = infile.readlines()

# Filter every other line, starting with the first
filtered_lines = lines[::2]  # Take every other line starting from index 0

# Write the filtered lines to the output file
with open(output_file, "w") as outfile:
    outfile.writelines(filtered_lines)

print(f"Filtered lines have been written to {output_file}")

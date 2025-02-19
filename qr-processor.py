import os
import argparse
import qrcode
import base64
import zxing


def encode_file(file_path, output_folder):
    """Encodes the content of a binary file into QR codes and saves them as PNGs."""
    with open(file_path, 'rb') as file:
        binary_content = file.read()

    encoded_content = base64.b64encode(binary_content).decode('utf-8')

    max_size = 2937
    chunks = [encoded_content[i:i + max_size] for i in range(0, len(encoded_content), max_size)]

    for idx, chunk in enumerate(chunks):
        qr = qrcode.QRCode(
            version=40,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4)
        qr.add_data(chunk)
        qr.make()

        img = qr.make_image(fill='black', back_color='white')
        img.save(os.path.join(output_folder, f"qrcode_{idx + 1}.png"))

    print(f"QR codes generated and saved to {output_folder}")


def decode_folder(input_folder, output_file):
    """Decodes QR codes in a folder and reconstructs the original binary file."""
    decoded_data = []
    reader = zxing.BarCodeReader()

    png_files = [file_name for file_name in os.listdir(input_folder) if file_name.endswith('.png')]
    png_files.sort()

    for file_name in png_files:
        if file_name.endswith('.png'):
            file_path = os.path.join(input_folder, file_name)
            barcode = reader.decode(
                file_path,
                try_harder=True,
                pure_barcode=True)

            if barcode:
                text = barcode.parsed
                decoded_data.append(text)
            else:
                print('error!')

    reconstructed_content = ''.join(decoded_data)

    binary_data = base64.b64decode(reconstructed_content)

    output_file_path = os.path.join(input_folder, output_file)

    with open(output_file_path, 'wb') as output_file:
        output_file.write(binary_data)

    print(f"Original file reconstructed and saved as {output_file_path}")


def main():
    parser = argparse.ArgumentParser(description="Encode and decode QR codes from files.")

    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '-e', '--encode',
        action='store_true',
        help='Encode a file to QRs')
    action_group.add_argument(
        '-d', '--decode',
        action='store_true',
        help='Generate a file from a group of QRs')

    parser.add_argument('-f', '--file', type=str, help="File to encode / file to recreate")
    parser.add_argument(
        '-p', '--directory',
        type=str,
        help="Folder where QR codes will be saved or read from",
        required=True)

    args = parser.parse_args()

    if args.encode:
        if not args.file:
            print("Error: input is required for encoding.")
            return
        if not os.path.isfile(args.file):
            print(f"Error: The file {args.file} does not exist.")
            return
        if not os.path.exists(args.directory):
            os.makedirs(args.directory)

        encode_file(args.file, args.directory)

    elif args.decode:
        if not os.path.exists(args.directory):
            print(f"Error: The folder {args.directory} does not exist.")
            return

        decode_folder(args.directory, args.file)


if __name__ == "__main__":
    main()

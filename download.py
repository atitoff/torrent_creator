import requests


def download(url: str, download_extension: str, file_path: str, show_progress_bar=True):
    try:
        with open(f'{file_path}{download_extension}', 'wb') as f:
            # Get Response From URL
            response = requests.get(url, stream=True)
            # Find Total Download Size
            total_length = response.headers.get('content-length')
            # Number Of Iterations To Write To The File
            chunk_size = 4096
            chunk_size = 65536

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                full_length = int(total_length)

                # Write Data To File
                for data in response.iter_content(chunk_size=chunk_size):
                    dl += len(data)
                    f.write(data)

                    if show_progress_bar:
                        complete = int(100 * dl / full_length)
                        print(f'{complete}%')
    except KeyboardInterrupt:
        print(f'\nDownload Was Interrupted!')
    # cursor.show() # Unhide Cursor If You Have Previously Hidden It

# Example usage :
download('https://github.com/atitoff/torrent_creator/releases/download/0.10/lib.7z', 'lib.7z', r'D:')
# Downloads The Atom Installer With Filename Installer.exe to Desktop
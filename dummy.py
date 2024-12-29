import subprocess


def download(url):
    """Download a file using wget."""
    try:
        result = subprocess.run(
            ["wget", url], check=True, text=True, capture_output=True
        )
        print("File downloaded successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while downloading the file.")


if __name__ == "__main__":
    url = "https://deneginepote.org/"
    download(url)

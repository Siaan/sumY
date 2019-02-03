from google.cloud import storage

class Cloud():

    def __init__(self, dataset = "simulations"):
        self.APIKEY = "innate-solution-180816-a14c920252690.json"
        self.projectID = "innate-solution-180816"
        self.dataset = dataset

    def upload_blob(self, bucket_name, path, destination_name):
        """Uploads a file to the bucket."""
        storage_client = storage.Client.from_service_account_json(
        self.APIKEY)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_name)
        blob.upload_from_filename(path)

        print('File {} uploaded to {}.'.format(
            path,
            destination_name))

    def download_blob(self, bucket_name, source_name, destination_name):
        """Downloads a blob from the bucket."""
        storage_client = storage.Client.from_service_account_json(
        self.APIKEY)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_name)

        blob.download_to_filename(destination_name)

        print('Blob {} downloaded to {}.'.format(
            source_name,
            destination_name))

# def check_update(self):
#     url = "https://api.github.com/repos/WLMY714/98assistant/releases/latest"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         print(self.version)
#         for index in data:
#             print(index, ' : ', data[index])
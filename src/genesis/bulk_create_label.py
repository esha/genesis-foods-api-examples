import configparser
import os
from datetime import datetime
import requests
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Retrieve the output file path from the configuration
output_file = config.get('files', 'output_file')
output_csv = config.get('files', 'output_csv')

# Retrieve options
food_type = config.get('options', 'food_type')
output_limit = int(config.get('options', 'limit', fallback=10000))

# Ensure the file is written to the local directory
file_path = os.path.join(os.getcwd(), output_file)

SKIP_FOOD_IDS = [
"ecd5efce-b9d5-4b64-5ef8-ee69ecb67fee",
"93aaf2e7-ae95-4eba-5ef8-ee69ecb67fee",
"1cfe648b-2695-45c5-5ef8-ee69ecb67fee",
"8ddec5c8-da08-4507-b6f6-04a5d1e46f66",
"6873041c-b024-44ce-5ef8-ee69ecb67fee",
"739c2e88-8417-47b6-5ef8-ee69ecb67fee",
"f3d17c7c-0de7-4615-5ef8-ee69ecb67fee",
"b3a17dd8-8e14-4cda-5ef8-ee69ecb67fee",
"2dd95115-34d2-4fd2-aae0-20fa5a1a82ad",
"738bcb82-8c74-4bea-bb2f-51fa988a551b",
"e7bf6a50-9f48-4f86-bc89-0983242f5bb0",
"3fc1388f-a351-43af-5ef8-ee69ecb67fee",
"b98c17fc-f336-49a2-5ef8-ee69ecb67fee",
"6048571c-c02f-450d-8dbb-4e85b2dd571e",
"315a2e78-9e61-4e6f-5ef8-ee69ecb67fee",
"f3d17c7c-0de7-4615-5ef8-ee69ecb67fee",
"8edf32fa-4c64-414f-5ef8-ee69ecb67fee",
"ecd5efce-b9d5-4b64-5ef8-ee69ecb67fee",
"8008ab43-1596-49ae-bce1-55d5f1609d19",
"dbe5d5cb-eb4f-4af0-881f-99f43c5d6302",
"f9f736eb-e23f-4913-b9ca-fba63ac7dbd7",
"6cc78bc8-2219-4f7a-a13c-4b1cb7783c85",
"5f9ea5b9-06d3-4772-835c-41399168cde8",
"92542e38-120f-43f0-b09c-576d9e8a8cd0",
"1c03b029-5536-4295-8f4d-0edbe4c8b0ed",
"5240d4f9-f44f-4cf6-abf8-f52fcf7a5930",
"aef5e50a-77c5-40e3-9ac0-e51a48f6ebbd",
"da97e015-095c-4b62-9292-2834be1a81dc",
"ed473649-8877-4323-a8da-548b12e1f6ed",
"27fd3c3a-1ad0-47f3-a351-e1725bde7729",
"e0b0b049-c683-4a12-861a-612fbcf80131",
"d34cd88f-45eb-4bb9-a035-76a41101ec74",
"04f9dff8-726f-42b3-903e-c95d212d35de",
"403aa833-3fa6-4eeb-b908-55a9808bd4b4",
"1ff46b65-f127-4073-b3df-40724a74f84f",
"bd5f33c9-a7da-4cc0-a8a9-788e29314dea",
"504a3517-40e2-4dad-9f6b-f7d1fb1102c9",
"5a722a69-3a74-4118-a213-77f5ec0e4f8f",
"1b2fbe19-9bc8-412a-8661-140d0aa3f668",
"5bf15c0c-cc0d-4f41-a21c-81fb0693bd82",
"f3231aa8-da4e-438d-816b-9f86d9107f82",
"8c4f81b9-8831-42c5-af1d-f2a969e78c2f",
"84e2c5d9-fb7f-4bad-8539-5476df223c54",
"2045f9a5-6e85-4159-9947-e8e0d693be39",
"c085dca4-2b0b-4d70-b17e-63962772467f",
"145642f1-5e1c-43a8-8503-5732ebbae958",
"25a5661d-271f-4bb7-a313-da1517f8d565",
"1f6e2971-c2af-4fac-a583-0ea1f5967a21",
"fdbd6cf5-09ef-459f-ba7b-5fcef2528dc8",
"aa5a5d48-ee3c-44df-b7f7-6b52ca763c8a",
"7a4aa235-b710-4d4e-aaba-9b17c50e0c08",
"ee2dace6-61f5-439d-80c5-62b3933ac2b6",
"d2194d3c-51bc-47dc-a111-02af2c0b6fc3",
"c09c79b8-ccd5-4c6e-86af-9b0560cdacfb",
"490397c7-a14f-4de7-9c81-5643785c7c99",
"43d48284-b823-4fa9-83a3-b040845692ba",
"b2647c76-ac3a-4969-85e0-a83d8dda3d19",
"633ca8ba-6b53-4b94-b82c-11b7bfc2bc0d",
"c2f867a6-22f4-485d-a1d5-64bb6cc621ae",
"3145a58b-5827-42ee-af77-84fd434d987b",
"94acdcdc-ef09-4702-989a-e2b87169979b",
"ddd56585-a586-4984-9b99-c5ab313ad673",
"9914c5e0-1c74-4fc3-b6d6-ebca138234c1",
"7b17b53b-920a-411f-b237-d05a69575a86",
"01f2e8b1-47f3-41a5-85c1-5409065532bc",
"232f22a0-6901-4698-9c5d-9ce7fe34603a",
"a8051174-5750-4183-bfa6-b811c5e35ae7",
"6e6863e8-6596-4414-b2d9-d47eaca469e2",
"4b9d10c4-1cd2-46a0-8434-074a932aaf1b",
"80315836-63f9-4bba-adb1-25a3091af037",
"91c85cad-4ecf-4fb3-a286-f89dd28deb28",
"bd9eccb1-5f5f-49fe-983f-fb7f7ded39ad",
"152f411f-2bcd-42f0-8e76-dbc2e2f8e456",
"335c2e56-699e-4d49-9322-820f331eaeb7",
"6b5eac43-71fc-4d72-aa73-99c32dd3db08",
"96875bb1-b55a-4a4f-8449-7e3621239932",
"8d4d70e6-a3b1-4fa3-9df1-0cd2af6f67bb",
"f200e2c7-c752-44dc-9e13-cd78dde04fe0",
"b8aac994-8479-4d89-9670-f7e22b82dbb4",
"41b17eb2-4b48-4c10-b3cb-bb8946067941",
"b1117f13-9a70-4e20-93d3-f1822fbfe87b",
"cd50bc93-ffdb-4068-a0de-f26c6f4f17e9",
"82acaa7c-44ac-4557-96fd-40558ebf87e3",
"79ac692a-6b78-4943-b12b-2ffc1aa6af52",
"1a7789d0-8657-40cc-b669-f9da4cea3c7d",
"581adfdf-a8ba-4a5c-b894-a69d46ae764a",
"3b98fb14-ff4a-42d4-8550-37a3592f59b9",
"bcf33680-f5ab-4d1c-9799-c92f749d102a",
"219000a0-0272-428f-8895-f76e1f99df33",
"df32cbd1-3a04-4173-b6fc-af951cdf2ebd",
"b521c31b-5709-4ef3-9bd9-c25a73d32cb3",
"b91f51e6-52b0-419f-b74d-8c2337ea925a",
"78eaafbb-1348-4ebe-ad1e-936a04e8c089",
"a18a5b74-9fb3-43e1-b472-b21236961a50",
"a84a91d8-c184-45f0-a118-97daf3d9429f",
"3441ac0f-e213-4ce3-9ecc-18c190c190f0",
"08793367-1221-4bba-b3bf-be14123fe38f",
"be7e5938-f671-41e9-9a5c-047b12a83346",
"d52197c2-93a2-4963-b848-4b918fcc13f0",
"583980fd-756d-4b70-96cc-3d76634d5d67",
"9e38bbb0-1f76-447b-8650-332b4188764f",
"2d44d811-af37-4464-bb75-0eb1d35ea01a",
"4e98377b-4581-4f4c-b4c7-9cc9b7da3fe5",
"359e1b77-15af-431d-b22e-86c152d20862",
"4d7603cc-50fd-487b-9b98-95d60c6addb0",
"e2be5718-b7d8-4911-89f7-2673b1987a4a",
"03b0d70e-d801-446d-8b7d-3fecffd99725",
"7e2c4ca1-dd1c-4fe6-90d0-8a8281103e3b",
"1bef28e2-de60-4487-b1ec-a5ed39c195d9",
"3963955d-006e-4e63-bec7-cab73e091e19",
"e733e2ac-e1e5-4326-986b-0db25113498c",
"16b5c213-68c4-4d12-bf79-87e91de30a7b",
"99126a66-2fb0-438d-82a2-d8adca9a000b",
"f7c1e04b-9269-4ff9-8713-a703fcd4b839",
"8ea0441c-8f9a-46a0-a588-0aa0605fb662",
"1d192595-4969-4c48-aebb-ee7e3aedbd30",
"65ae15c4-8c5e-4762-887f-da74ecd77fe8",
"b2f4fdad-b1e0-4f63-b4c3-7756d0376685",
"3caab32d-fef8-4a66-bda4-0bd37c209eea",
"e51ac47d-5096-44da-9f48-3e51167975da",
"df292cdf-4642-48fc-b84b-5c21fc4e4983",
"8dbb8612-43f2-4496-98cb-e97c8224ae7c",
"bf38c87f-8d45-41fb-afc1-b9637938be2f",
"c5c0ad62-fd52-4744-b835-d212fd838686",
"7c6e065d-5c0c-4ea3-85fa-b24d1ed878c7",
"8a51a774-9c65-4318-8e59-7721b995b458",
"523c75bd-e5f7-4443-b38f-b3282276b4d0",
"b5f09064-f288-4cb0-9cf7-0161ea663db6",
"d68a627d-bfdd-4e8c-9d5d-120e2eaf79ca",
"2c4f792d-57b5-4dea-a736-52d851263753",
"5cd58712-64c3-4550-bff7-1d74f6b62d7b",
"7e153575-0da8-4249-967f-9011b88526bb",
"f67991ad-8612-4250-8beb-63224608a74f",
"94efde4a-eb91-44d9-b1db-9968dc0626a2",
"10a244d1-9783-4fed-8820-a04de874f01a",
"842a9fa7-7409-4095-8d6e-7135736359b0",
"a8663172-0952-494d-8ad7-aecb9b9e3b84",
"72cb7054-8b30-4892-8ca7-c862f3bd3ddc",
"fac0fb02-5000-4ed3-b9bd-459d4e7312dc",
"baf52f4e-5245-47c5-9486-e115d75759b5",
"9432df50-8717-43eb-b3fc-574f38f40577",
"7f114ee2-3bde-4888-b4df-3e2e3aa3380d",
"5ef85076-b09d-4351-b5da-b9f3d2fd5ec8",
"9e30b818-278f-4012-9ee8-67c5bf3d0391",
"0ae6aeb9-fb12-46b5-83b5-cfd7486c7d16",
"f438afef-972b-4576-8fec-8965bb8b2952",
"ef9b3a96-a200-45d9-82f1-1a0fc54e47e4",
"a5b62f95-c5c1-4897-879e-cd4201290b32",
"fad23d4d-5264-4f9e-ba5f-c3ae651ca340",
"c4dbca51-2b21-480d-bccf-8a2090082dad",
"a84687f9-2fae-4377-a42e-d8d11ba0b157",
"ff442435-2a3f-4882-aee0-9e364660a8be",
"fa9ad8e6-a4a4-4556-9018-a67b03632537",
"59e9a162-869b-4ac7-b2d1-3ada40adb590",
"2211d5fa-87db-4dde-9ca5-da2a15aba103",
"ae8b7a4f-3d33-4ae1-93dc-a99dc1f560e4",
"1fe009b6-ae48-4720-b8bc-f38554cea9e8",
"ce8b5aab-7ad3-41d2-b8b2-83e3afda9868",
"17228e27-75fb-47df-91b0-cf7f58ec3b9b",
"5c57c07c-85fd-45d0-9e9d-5a0e541ae6fd",
"04059580-1daa-4f44-9675-87f1c5430f77",
"453c03cf-c3c2-4492-9290-cd17289b5aab",
"d5f2441d-7dcc-43e5-b4f9-d41163bec1e0",
"5dcdc841-9ea3-4c4d-b6a5-82a4c7008790",
"30a2c7ae-04c2-433f-8333-f8e851b67aca",
"90d10c91-875a-4e29-b2ca-331b5266739a",
"d3c59da8-df0b-4911-a55c-dacce6981967",
"9ae3fa6b-5a70-45b5-b507-0e0680594084",
"056d5ae8-404b-4ce0-8b59-9f58f9f3e622",
"da526d9b-8d84-44e4-bd8f-f1042f7c215c",
"f1acd61b-2d5f-489b-9b01-5015c8712ab3",
"ecdc0f5d-c19e-49a0-8a02-045580b15230",
"6726327d-2954-49f5-9f92-bae3ede1e6e0",
"d250288c-5e4c-4f73-ac42-f7a010941805",
"58d171ff-73b0-4768-b885-75b6e4a7b804",
"ce31d2a6-71a1-4bd3-af0b-5570c683412a",
"a6a9b684-9bab-4906-a3e5-169db465f0c2",
"e5e159a3-1ddd-49b0-93ff-fbe8c6b75fa9",
"f557ee19-fae7-40d2-b672-e0b6dbf06417",
"0318e9e1-f3d7-4379-b4c3-a46211590b1d",
"dc973721-b6f4-4949-a3de-64be94fd3752",
"9347287d-c022-4f34-b2b0-439348b13f34",
"69de99a0-078c-45e5-a468-9492143a7ca1",
"2463845c-f9c2-4fc1-8f17-3b107ab43d4c",
"642f2d06-ec08-4556-bbec-d9c4b12bb6dc",
"63291417-0acf-4041-b7cd-02d8a78d3656",
"037fddd7-12d1-4ea5-ac64-70e80d2e9825",
"93db2d15-129f-4f5b-892f-d8d8b00fbdbf",
"2e42857c-b0a8-49e3-b749-e86b97e87563",
"0457b1cd-a937-4fe6-a99d-4c91688b3eaa",
"fcf3df5f-ce96-43e2-8f1b-35702b54a194",
"1b38ba5c-088a-4e07-b0dc-2ea37d19a803",
"b4306484-b1c5-4b37-89c1-f87eac7257f2",
"21fe8ce8-ca19-47f0-bd66-bae70eff8f46",
"38937b16-f6fa-4f1f-bde8-f1771f83a3ad",
"89024dca-0f3d-4016-91b5-f71b8159e660",
"9a7f7a27-02de-47c6-a663-62996996c81e",
"11035d98-c6fd-49f6-97e2-365699baf469",
"038b3f37-7aae-4374-981e-01b04c72a52e",
"166e3d1b-270c-4fc2-9b60-5c206830f382",
"677e6089-b0fe-42fc-937c-fdaf2a70a6db",
"0b40cba5-48bb-492b-b5e3-4ef94631813a",
"563612b4-c4b8-45a2-969c-fbe1ee7069fc",
"e40d11c0-a5d3-44c6-8ce0-8eb18e52084f",
"2cbf952c-748a-4eb7-88ea-c9ea4d18d216",
"1f182f66-4b61-44d5-b6f3-9535a30c5b72",
"4bd818a4-51dc-40d9-8c9d-170187f146fc",
"24eb7fe6-f3a4-4565-a882-3e03f40f6aed",
"23ecc10d-a761-457f-8c17-fbc3213e7767",
"1c1d6575-1072-4250-8b37-8f58743ab76c",
"2750b69a-f993-475c-8008-c620e3e7c584",
"b79ab0b0-788c-4306-b3aa-e235f2600eb9",
"d6153ac9-284f-4eaf-8b94-d8b271ef5803",
"b1632d5d-c028-43af-ad31-d4d3fc5fbcb3",
"b02795b6-a4ef-4221-8c2d-c8233e3ea55a",
"3f4a71bd-94d9-4c52-b6c2-7c82a8d7a8c1",
"542660d2-697a-471d-87ae-4482055b97fa",
"9734fc45-fedf-43ad-b833-aeacd7cb7a05",
"f19d3a6f-ef5d-4a29-852a-b384f7e9d76f",
"d1138a9c-a8f2-4a80-8f5f-ad4188d7d94c",
"5584f539-e64b-4299-9451-2326143ba1f2",
"7207a983-0c18-4a43-a5d1-ced46e44ed26",
"0fc26538-5102-4f17-b34b-4ffbda88c664",
"8dd04fcb-bb1b-4f97-ac21-f0579236de25",
"fc8a25f2-557c-4108-aaad-0cb5e4a08cc6",
"16e4dd73-7b3f-46a7-8075-636eec52c5e8",
"59a2a537-7e8e-45c8-aa47-bc5be66e8e15",
"ffa19879-990c-46fa-b525-3401cf31a7fc",
"1ceba022-5ef3-41e2-b2b5-8b609cd5acd3",
"d64b7879-7cff-47d9-9aa9-1442a51adfe8",
"a0692c8d-9b72-4dbd-af9d-59f4e1821e8c",
"abe863eb-e750-4f37-8811-ee06249c177e",
"f905d4e5-5efc-41a1-ba0d-a3a3a62500a4",
"6462b174-7a0e-469d-90f8-a0f661922308",
"94f35822-cf5d-4f8d-a5e3-87ccead369ad",
"e015c4f1-ec10-4576-b5d5-0bd96392ed0d",
"4998bf3c-5b51-4561-ad70-77f671a42258",
"e4d7c429-6e34-4ace-8fd9-09714ff22550",
"31efdfc5-b27a-4309-923b-6d7bb570cbcf",
"d6a97ae2-dd12-4516-ad48-9481bc32a344",
"5e37a3a6-1578-45b0-8f5f-353996e0593c",
"f0efc5cf-e31c-4979-96cd-3c9db1f3c36a",
"a3744785-aa50-4c23-8ed9-ff07d2addb71",
"1e014250-eb27-4630-bd46-15ff694875ae",
"2317655d-39eb-4d5f-8d0f-ec67dfd2c0b4",
"f091310d-bef7-4a87-b25c-0448b092ee4b",
"37b10043-1470-41e9-b62b-e555053b187c",
"5a97ab50-800d-4626-ba08-9042e6a1ad76",
"757c3e61-110a-4ad0-ae51-ef4ba90aab94",
"d3442787-f4d2-4970-855e-b8160beebcd8",
"41425ecd-4d30-4c4c-bfa9-bb99af48f962",
"b7f1f4de-1449-45ab-8ff9-8340a1b4a6d3",
"9849cb70-8979-448c-9cec-efa1f73a9667",
"67f91dd3-f15d-4cbd-980f-3f6c365dd3ca",
"ed074cde-4330-4992-a1f9-e9c487f7e4bb",
"941bef5d-ff66-4de2-9954-8fb1a51f9a55",
"2a1c3fa0-4dc6-4884-8612-e1788842d710",
"a0d0eeda-fcd8-4446-b929-425818a1b425",
"7c3734ae-680b-405c-8769-04525bdd5078",
"192eb160-bf71-4188-b4f8-79f9c9a13da1",
"1509bb9f-5c72-4b70-b51b-e86270f40cbe",
"7b409a5a-448b-4ee5-a316-ac6bf5c89470",
"c02fdf18-eacf-4930-bafe-d03a374e62e7",
"03347343-8347-4b98-9243-b6e79251ba35",
"8c0f21a3-7a66-42a5-a9bb-6879e49226a9",
"e15c1f7b-7529-4428-98fe-9eeff00c4115",
"fc977f52-f2eb-4986-a3f8-b633abde4d45",
"c316234e-20ea-4b46-85df-9fe66fa62116",
"9b9417be-4997-4862-8183-058cdd958d7d",
"0972bb5f-044e-4869-8b6e-37ca5bf7d269",
"92bdeb29-4a6b-4553-9a02-7cffe0203e85",
"6b5ebdbc-907e-4058-ba7f-8b2266304c9e",
"de94001c-4d61-4f2e-af05-ef295f6216e3",
"a1d99508-2f37-4acc-949e-7a9ea3b4db73",
"918aed35-a949-463f-9f0b-7a5ad6c93126",
"c579f2fe-3a46-4b52-9786-edc53244e72a",
"ca8bb9ad-ca00-4d21-abec-74fa41c0cb2a",
"08296435-8fb5-45cd-9860-7e34b470e518",
"d8e616ae-7ed4-416b-906d-686a978599b1",
"ba336307-daf0-4f65-a875-b9a9a742f89f",
"20d08885-a627-4550-9ac6-6a728425d9f1",
"00ffe494-a4d6-450e-9877-d925c4abf9bd",
"e9a034bf-3156-4456-8abe-f532528a0c3b",
"56719333-f3ff-493e-826a-cf341fd69f37",
"c4e4bdb5-cfa4-43c1-85a9-927af45daff5",
"beaaf114-20dc-4624-a36f-3f9bab362a53",
"db725aa3-fd39-48a3-ad95-b64bb1cba14b",
"30c446c2-8027-4518-ad76-762283c7aa5a",
"ba38c1ca-b2e0-420f-8423-de45aeafcaec",
"37e6c315-8398-4463-b4ac-ceffd78d9435",
"48fd8b63-9409-4d1c-9578-32b714da4ccf",
"2cdea4e1-5244-43b2-a2e2-e41754e178e4",
"7e46d77b-c881-493c-adb4-a7604664170e",
"ebed1e9d-507f-40f9-8b6b-5cd2b5eed3d9",
"319c8503-c8fb-4a24-990a-d2fc4e3290bf",
"b348c0cf-a33b-44db-8021-e9829465e138",
"848bdc7f-f443-44b8-864a-fb94a0f72f00",
"088cade3-b6bb-4a8a-8ae4-2eac11d14b59",
"dad2d185-5dd5-4c86-b82b-1c60953b9d59",
"d48d310c-7ca9-4fdc-907f-93405aa9da1b",
"91a50ec4-4afe-4304-951f-ca33d30deb7b",
"b5391910-a102-4831-b54a-d8acc9f175ee",
"be456d84-83c0-4621-a061-0b0a17e4f79a",
"6e00c332-0a39-4e5d-adc0-dd28a739e8a2",
"48020ae4-3be8-48d9-b663-2dccca29ccf4",
"230ac331-bacb-4171-bd35-04acc72b80d8",
"b1e1cd50-7368-41c1-849b-1c340fe9c98d",
"0781f2d5-a3f6-4cd3-9660-6ea01d70a3a9",
"80b575e5-7bf8-41b9-a3a1-af6fb7e17cd9"
]

# Delete the file if it already exists
if os.path.exists(file_path):
    os.remove(file_path)
    logger.info(f"Existing file '{file_path}' has been deleted.")

# Define the headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

search_query = """
    query ($input: FoodSearchInput!){
        foods {
            search(input: $input) {
                foodSearchResults{
                    id
                    name
                    modified
                    created
                    versionName
                    eshaCode
                    foodType
                    product
                    supplier
                    versionHistoryId
                }
                totalCount
                pageInfo{
                    cursor
                    hasNextPage
                    startCursor
                    endCursor
                }
            }
        }
    }
"""

tags_query = """
    query ($input: GetUserAddedFoodTagsInput!) {
        tags {
            getUserAddedFoodTags (input: $input) {
                tags {
                    id
                    name
                }
            }
        }
    }
"""

create_us2016_label_mutation = """
    mutation ($input: CreateUnitedStates2016LabelInput!){
        label {
            unitedStates2016 {
                create (input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

create_ca2016_label_mutation = """
    mutation ($input: CreateCanada2016LabelInput!){
        label {
            canada2016 {
                create (input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

create_eu2011_label_mutation = """
    mutation ($input: CreateEuropeanUnion2011LabelInput!){
        label {
            europeanUnion2011 {
                create (input: $input) {
                    label {
                        id  
                        name
                    }
                }
            }
        }
    }
"""

create_mx2020_label_mutation = """
    mutation ($input: CreateMexico2020LabelInput!){
        label {
            mexico2020 {
                create (input: $input) {
                    label {
                        id  
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_us2016_label_mutation = """
    mutation ($input: SetUnitedStates2016LabelItemsInput!){
        label {
            unitedStates2016 {
                setLabelItems(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_ca2016_label_mutation = """
    mutation ($input: SetCanada2016LabelItemsInput!){
        label {
            canada2016 {
                setLabelItems(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_eu2011_label_mutation = """
    mutation ($input: SetEuropeanUnion2011LabelItemInput!){
        label {
            europeanUnion2011 {
                setLabelItem(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_mx2020_label_mutation = """
    mutation ($input: SetMexico2020LabelItemInput!){
        label {
            mexico2020 {
                setLabelItem(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

def run_query(graphql_query, variables):
    """Run a GraphQL query against the Genesis API with variables."""
    response = requests.post(
        endpoint,
        json={'query': graphql_query, 'variables': variables},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Request failed with status code {response.status_code}")
        logger.error(response.text)
        logger.error(f"Endpoint: {endpoint}")
        logger.error(f"Query: {graphql_query} \r\n Variables: {variables}")
        return None
    

def search(graphql_query, food_type):
    variables = {
        "input": {
            "searchText": '',
            "foodTypes": [food_type],
            "itemSourceFilter": "Customer",
            "archiveFilter": "Unarchived",
            "versionFilter": "Latest",
            "first": output_limit,
            "after": 0
        }
    }

    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} results.")

    return result

def search_by_tags(graphql_query, food_type, tags):
    variables = {
        "input": {
            "searchText": '',
            "foodTypes": [food_type],
            "itemSourceFilter": "Customer",
            "archiveFilter": "Unarchived",
            "versionFilter": "Latest",
            "tagsFilter": tags,
            "first": output_limit,
            "after": 0
        }
    }
    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} results with tags {tags}")

    return result

def get_tags(graphql_query, tags):
    variables = {
        "input": {
            "first": 100,
            "after": 0
        }
    }
    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        tags_data = result.get("data", {}).get("tags", {}).get("getUserAddedFoodTags", {}).get("tags", [])
        matching_tags = []
        for tag in tags:
            for tag_data in tags_data:
                if tag.lower() == tag_data.get("name", "").lower():
                    matching_tags.append(tag_data)
        return matching_tags
    else:
        logger.error(f"Failed to find tags {tags}")
        return None

def create_us2016_label(graphql_query, food_name):
    label_name = f"{food_name} - US 2016 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical",
            "recommendationProfile": "Adult"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("unitedStates2016", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create US 2016 label for {food_name}")
        return None
    
def create_ca2016_label(graphql_query, food_name):
    label_name = f"{food_name} - CA 2016 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("canada2016", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create CA 2016 label for {food_name}")
        return None
    
def create_eu2011_label(graphql_query, food_name):
    label_name = f"{food_name} - EU 2011 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("europeanUnion2011", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create EU 2011 label for {food_name}")
        return None    
    
def create_mx2020_label(graphql_query, food_name):
    label_name = f"{food_name} - MX 2020 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("mexico2020", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create MX 2020 label for {food_name}")
        return None

def add_recipes_to_label(graphql_query, food_ids, label_id):
    variables = {
        "input": {
            "foodIds": food_ids,
            "labelId": label_id
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("unitedStates2016", {}).get("setItem", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to add recipe to label for {food_id}")
        return None
    
def add_single_recipe_to_label(graphql_query, food_id, label_id):
    variables = {
        "input": {
            "foodId": food_id,
            "labelId": label_id
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("europeanUnion2011", {}).get("setLabelItem", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to add recipe to EU 2011 label for {food_id}")
        return None
    
def bulk_create_for_all_recipes():    

    search_result = search(search_query, food_type)  # Food type from config
    if search_result is None:
        logger.error(f"No results found. Exiting.")
        exit(0)

    # Get the total count of search results
    total_count = search_result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
    logger.info(f"Found {total_count} {food_type} items to process.")
    
    # Ask user about label types after search results are known
    print(f"\nFound {total_count} {food_type} items.")
    print("Available label types:")
    print("1. US 2016")
    print("2. CA 2016") 
    print("3. EU 2011")
    print("4. MX 2020")
    print("5. All label types")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            break
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    # Define which label types to create based on user choice
    label_types_to_create = []
    if choice == '1':
        label_types_to_create = ['US2016']
    elif choice == '2':
        label_types_to_create = ['CA2016']
    elif choice == '3':
        label_types_to_create = ['EU2011']
    elif choice == '4':
        label_types_to_create = ['MX2020']
    elif choice == '5':
        label_types_to_create = ['US2016', 'CA2016', 'EU2011', 'MX2020']
    
    logger.info(f"Selected label types: {', '.join(label_types_to_create)}")

    try:
        # Create labels and add recipes to them
        for food in search_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", []):
            food_name = food.get("name", "")
            food_id = food.get("id", "")

            if food_id in SKIP_FOOD_IDS:
                logger.info(f"Skipping food ID: {food_id} - {food_name}")
                continue
            
            # Create labels based on user selection
            if 'US2016' in label_types_to_create:
                us2016_label_id = create_us2016_label(create_us2016_label_mutation, food_name)
                if us2016_label_id:
                    add_recipes_to_label(add_recipe_to_us2016_label_mutation, [food_id], us2016_label_id)
            
            if 'CA2016' in label_types_to_create:
                ca2016_label_id = create_ca2016_label(create_ca2016_label_mutation, food_name)
                if ca2016_label_id:
                    add_recipes_to_label(add_recipe_to_ca2016_label_mutation, [food_id], ca2016_label_id)
            
            if 'EU2011' in label_types_to_create:
                eu2011_label_id = create_eu2011_label(create_eu2011_label_mutation, food_name)
                if eu2011_label_id:
                    add_single_recipe_to_label(add_recipe_to_eu2011_label_mutation, food_id, eu2011_label_id)
            
            if 'MX2020' in label_types_to_create:
                mx2020_label_id = create_mx2020_label(create_mx2020_label_mutation, food_name)
                if mx2020_label_id:
                    add_single_recipe_to_label(add_recipe_to_mx2020_label_mutation, food_id, mx2020_label_id)
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)


# This is pretty rudimentary and brute-forcey, but it works for now. 
# Ideally its changed to allow the user to map a tag to a regulation since their tags may not align with these options.
def bulk_create_for_all_recipes_by_tag():
    # We need to ask the user for a list of tags they want to include in their search, 
    # we then can look up the Id of those tags via the api so we can include it in our search results
    print("What tags do you want to include in your search?")
    print("Enter a comma separated list of tags. Default: US, Canada, Mexico")
    tags = input("Enter the tags [Use default, press enter]: ").strip()
    if not tags:
        tags = "US, Canada, Mexico"

    # Split the tags into a list
    tags_list = [tag.strip() for tag in tags.split(",")]
      
    matching_tags = get_tags(tags_query, tags_list)
    if matching_tags is None or not matching_tags:
        logger.error(f"No tags found. Exiting.")
        exit(0)
        
    print("Available tags:")
    for tag in matching_tags:
        print(f"{tag.get('name')}")

    search_results = []
    for tag in matching_tags:
        tag_id = tag.get('id')
        tag_name = tag.get('name')
        
        result = search_by_tags(search_query, food_type, [tag_id])
        if result is None:
            logger.warning(f"No results found for tag {tag_name}. Skipping.")
            continue

        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} {food_type} items with tag {tag_name}")

        search_results.append({
            'tag_id': tag_id,
            'tag_name': tag_name, 
            'result': result,
            'total_count': total_count
        })

    if not search_results:
        logger.error("No results found for any tags. Exiting.")
        exit(0)

    logger.info(f"Found results for {len(search_results)} tags")

    print("Continue with bulk create? (y/n)")
    continue_with_bulk_create = input("Enter your choice (y/n): ").strip()
    if continue_with_bulk_create != 'y':
        logger.info(f"Exiting.")
        exit(0)

    try:
        for search_result in search_results:
            tag = search_result.get("tag_name")
            for food in search_result.get("result", {}).get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", []):
                food_name = food.get("name", "")
                food_id = food.get("id", "")

                if food_id in SKIP_FOOD_IDS:
                    logger.info(f"Skipping food ID: {food_id} - {food_name}")
                    continue

                if tag == 'US':
                    us2016_label_id = create_us2016_label(create_us2016_label_mutation, food_name)
                    if us2016_label_id:
                        add_recipes_to_label(add_recipe_to_us2016_label_mutation, [food_id], us2016_label_id)
                elif tag == 'Canada':
                    ca2016_label_id = create_ca2016_label(create_ca2016_label_mutation, food_name)
                    if ca2016_label_id:
                        add_recipes_to_label(add_recipe_to_ca2016_label_mutation, [food_id], ca2016_label_id)
                elif tag == 'Mexico':
                    mx2020_label_id = create_mx2020_label(create_mx2020_label_mutation, food_name)
                    if mx2020_label_id:
                        add_single_recipe_to_label(add_recipe_to_mx2020_label_mutation, food_id, mx2020_label_id)
                elif tag == 'EU':
                    eu2011_label_id = create_eu2011_label(create_eu2011_label_mutation, food_name)
                    if eu2011_label_id:
                        add_single_recipe_to_label(add_recipe_to_eu2011_label_mutation, food_id, eu2011_label_id)
                else:
                    logger.warning(f"Skipping food ID: {food_id} - {food_name} - No label type found for tag {tag}")
                    continue

    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    logger.info(f"Starting bulk create label process...")
    
    print("Available Bulk Create Options:")
    print("1. Bulk create for all recipes")
    print("2. Bulk create for selected recipes by tag")

    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        if choice in ['1', '2']:
            break
        print("Invalid choice. Please enter 1 or 2.")

    if choice == '1':
        bulk_create_for_all_recipes()
    elif choice == '2':
        bulk_create_for_all_recipes_by_tag()
    
    logger.info(f"Bulk create label process completed.")    

    
    

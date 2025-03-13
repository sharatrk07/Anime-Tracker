import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key JSON
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "anime-progress-tracker",
    "private_key_id": "77b2636edbbbfa0a0fca1f16f021527f53de8e50",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCmmVEC+Bhm6FnD
DtDVctfa4oHk8DcwhVPS6/DMqmfJw2FushKLJjTZ5YXdQSXM9d1RFrkT20p/Nykv
NVSjc2/46SYD+qUk5M8ZDeeHptWoLPbfws3Mp+5iaZdR1XJb02JkyczGki9LJEht
L28Er57Dv85wL2wWhaPiyVzVJdnHn1hHa2zGvMb41HNLvYNkX22IL6pbSaX5yFg6
H5OtsUdeaJSlUJFbz6MIBzOBAo2CgLQufE451oGz+cA3h6bCm8l80J+yU7l3I6LO
3bgWbb2HqehoqGmiWEA3K/qph8ehcljWjHUdxjI8JNJ2UycXtqbeWerY0kYF89MC
l/vT7Hf7AgMBAAECggEAAQ3lD0gVch2JXxUZYvStkBXGd/5bTS/FejpLEzbk2eo3
NjraqB7n16Y6Y8W4gOsTh0S0z4dsu906f9NhcHixaOhwRXtf+eaG6lDOrUh8Zchj
mFwb90vrsaysMEXrdHsKcI/ow6NUyfQT9cpCUlRnQDQjzKJYucL2E2i68TJeUseI
IqIuutg195K3RIp7MSdl5VbcR/CuRe0lZ2AV5huiHJdriJ7RrqU4iRN77bilZNsy
x4wWhezZEKAt0H8c7ZwM9PRt255PExrnDDpkHvjFyPbmlS2oWZiGTVATZ6sY2ySu
Lw2EZo7ovm7Bu1uqC8V8/iEgfMWiVCPtl56qvfrjqQKBgQDoh5k8hy+7umYTvr9e
vb38E4rAPyzcKGERvYgzRSgbX96jshlrWDHxkYq0ocs9z7eDVK1R4/oBh23bBDo3
ZPe8G+ij9fFfFzn40fCJXYQmpbJgGLB8+Ro+JllT/ITenKYOJ+8bo+IiAIH2YRVM
aaFEzYhqJpYELg6aAEUq2KHqJQKBgQC3ahz7edt4bV/SXjHJr4Z/8DTOic2lmcvu
uBTh34uL5uDGVXjNn447duLAtcruUDFnc1eawiW22/yqTtYKeGbsNSFXBT3rDYBj
StemnjBawkTYtrKMC//kX29Sg/ZITKVI1JNmL7XUOsrMSt0bGbFTfMQJNxPzDhjo
od7LUJ5vnwKBgG1qUOqwWf+l6B5mZTo5YkpZD7MChyNZRMPKQWqOoh6vb93rEhb2
uxmGeJQihbYiJaIAmEWuVpedmE20oYgrVH8JSuDL+7XZAghZESwx+tsMoPCi7XkA
5h5UgTgJ3KO7Zk/G7rY82U1Sm9TJPfJkyePMKuJ4IaL54RkKA4HzycyZAoGAa8DV
ghAXFer7znU0Ps7175fJDkX7IPz3yCkxa3mPXAOprhtsuzCvuNOhZ6HltJg8ThB/
ORYyXfljuRJTwRb3MHIOQjd8Julpseu4QdTRh6B2HfNHdetezGYc2pdYSyVsPRtV
9US2SBa6KccZmuA/Q1MbQGaxO6veilz+rOeSDPUCgYA5f/5yJoW7wzDhFrWz+sR9
lcXe6NRbhKrRsr7GQGn8m26I2Cooq6ATuACd+q6i6Ng/juUi99ZO7qS7Ljv3BQr1
/FS3iAg7EqVSDXZ2kckvKZzymjnp7NxzDgQCqYAoaNEJWt9xHJLi/Y0HQmM+4uvw
2PYydB+Y2glPW8mfvdeR2Q==
-----END PRIVATE KEY-----""",
  "client_email": "firebase-adminsdk-fbsvc@anime-progress-tracker.iam.gserviceaccount.com",
  "client_id": "108088266466817496846",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40anime-progress-tracker.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})

# Initialize Firebase Admin SDK (Only if not initialized yet)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()
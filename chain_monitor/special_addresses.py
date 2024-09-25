from tronpy.keys import to_base58check_address
from web3 import Web3

from chain_monitor.web3 import get_logger

logger = get_logger(__name__)
WHITELISTED_ADDRESSES = {
    "0xB5Cebb87FF1a48cA28aBC25b4584FF5148d1808E": "Dunamis",
    "0x3dbB0d82b1E5224186f9E3E6b9429298b530B81F": "Dunamis",
    "0x14B3C2F915a25AB1a841CfA93a041A7F01Fc60F7": "Paretone Capital Fund LP",
    "0x0B59f0cdE121649D5fafFdBd534749B3bd0C0037": "Paretone Capital Fund LP",
    "0xe53a017B9fb097756b136D1C251740854165a03A": "Bastion",
    "0xe61b8dc9F28782BD67F491199732e3FbcA60d3dA": "Bastion",
    "0x9eb81a8Da86f30084367AbcFb6eA0A03e277ACe6": "Ecology Ltd",
    "0x987B8951d5b2700a1f718DAD6Bf62E7108160F28": "FalconX",
    "0x310962d9a743f1d9f153743b90B2121e040B42d8": "Quantamental",
    "0x0DC5fff38d83ad0f47FB4D9AEd89aFABC5e24C86": "Ho Hor",
    "0xCeF147a875C8085f5D725E232364676D59c5B3D6": "Amber",
    "0x20819B88b0D737D410C7DA01e102f7Dc2Bb92197": "Amber",
    "0x920e9163514b07EfA84DD248a58E6AD09D45211a": "Amber AI",
    "0x4864844EE5AEC82A44175b23c4b32545743B4aD7": "Genesis Block",
    "0x270cd0b43f6fE2512A32597C7A05FB01eE6ec8E1": "TrueTrading",
    "0x24F5D3CF7f5b8c941650B91eeD7036D986066c99": "QCP Capital",
    "0x75A33ba37d86A0fBd06970577017dEc18d896e15": "Subspace Capital",
    "0x44dD0fb90e355Ab0E2Bb59e8Db500CE6959B656f": "Huobi Labs",
    "0xA51b52a6D440085A3e6AcC5137b68929788D46F8": "KBIT",
    "0x1bff026A22E1CC46FFAc53E491A3e5591B2A80A5": "KBIT",
    "0x568cC6EcA34D56f5695B16Ff0250DFA77F247c47": "JC Asset",
    "0xd2C8740C70f3Dc7c42040d4e045844728B273E77": "JC Asset",
    "0x369FA58C1713f17cDF8396e9FdCC3b3cEADfB241": "JC Asset",
    "0xAAd2B92577B40F433536d07D1c050d1a4a50488d": "JC Asset",
    "0x6B1e6006587411c6a3A179bcf7f5EAcAa73284fE": "JC Asset",
    "0xF16C4DDB166e3a0D04E860497a1fD116b35C33BC": "Q9 Markets",
    "0xEC2cD3Fe353C8F4911a49fDa87e6778293D712fA": "DV Capital",
    "0x3Ad0D8cb4744F353C1D5e01030d02123146Eeb4C": "Legend Trading",
    "0x29FCE383c67D00954aC9367f6d3C8215989244eE": "Ovex",
    "0x17Ddc84bFB988452ADb561eD5f80eEa8ed48F848": "Alpha Node Limited",
    "0x1A35a6EB5987e1006b98852b63D16703CDf410aE": "Targetline OU",
    "0xD5DeE8195AE62bC011A89f1959A7A375cc0DaF38": "Bastion Worldwide Limited",
    "0x6cff1D0656D7eEA490B018b59D7f80e3a0455e5f": "Bitso International Network",
    "0xFA103c21ea2DF71DFb92B0652F8B1D795e51cdEf": "Symbolic Capital Partners, Ltd.",
    "0xFcBD6E6B491b4421B70cf7083F0069dD369aeb16": "MCA International Limited",
    "0x701bd63938518d7DB7e0f00945110c80c67df532": "Black Anthem Limited",
    "0x3DdfA8eC3052539b6C9549F12cEA2C295cfF5296": "Black Anthen Limited",
    "TA95AvP3UxekDH4qZcBrCkB3iA9xYkunAp": "Black Anthem Limited",
    "TDqMwZVTSPLTCZQC55Db3J69eXY7HLCmfs": "Black Anthem Limited",
    "TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5": "Black Anthem Limited",
    "TLRt2GZrfxBsYWjsh7wjmZbXT3WKMoEws9": "Black Anthem Limited",
    "TScVwVTjqoqPEJ6atnvGCtErWnCyNbzmUL": "Black Anthem Limited",
    "0x13873fa4B7771F3492825B00D1c37301fF41C348": "Black Anthem Limited",
    "0xB3f923eaBAF178fC1BD8E13902FC5C61D3DdEF5B": "Wintermute Trading Limited",
    "0xE0B2026E3DB1606ef0Beb764cCdf7b3CEE30Db4A": "Numerium3 Limited",
    "0x652Fc5b8686417BBf49F3eFab8cABE0CB6b1Ce05": "Stablehouse Ltd.",
    "0x81A3e936B4b6e6D85b54988B26ad5aa9da487b48": "Stablehouse Ltd.",
    "0x495f9f6C2d993cDcD4b5Eea7BEfF874A383D93BA": "Finconnect (Canada) Corporation",
    "0x5C1Ed2dc41bC1Cdb84F00d8BF20E934ffD1683df": "HIROOKA FAMILY OFFICE PTE. LTD.",
    "0x666308654cd4dD490221625DA53cbc18746dFF75": "Hehmeyer Trading AG",
    "0x7CEC0e6bBBAeD204045Df99E8C7cBa6c03Ebeb93": "Zenrain Technology Limited",
    "0x88029Fd62b3f88A809Bb059162aABD113294CE24": "OSL SG PTE. LTD.",
    "0xD9930047aD7325523f19F8f56268C46a8EA32bBB": "Dunamis Trading (Bahamas) Ltd",
    "0xb993D1C583b3905aD3acd3c1D44424eB462901a7": "ZenX International Limited",
    "TLgzBccs9c8hsLPneim5j4SSdqWSWPKMBy": "ZenX International Limited",
    "0x5fa4BC78D2eD857Fca158df5f64cFf3E690784d1": "Clerkenwell Master Fund, Ltd.",
    "0xB25b11E6df07699a3903461bb37F6272E129C869": "Plutus Lending LLC",
    "0xde98236DeF1A47dF794A86C2B4A2F4a0CDdAcb43": "OBFC Inc.",
    "0x2Ed2fcBEa82dD1a39fa5a534983E60a61720C22E": "Trigon Trading ",
    "0xb73F03038aC931dF745fDfF9C6d731C556Ee13da": "Stillman Digital LLC",
    "0x9dD4AEEBbc90aFCe21a7119Ad86df1F9c7dE633a": "Stillman Digital LLC",
    "0x49a160E521c804e5BD69B23F24D77020072E4aAb": "Dunamis Trading III",
    "0x66f839412f778E504934Cc82207C71978b0Da116": "Lightning Investment Holdings Limited",
    "0xcBa8EBd7aAA107E5550B430F40d0f083501956aF": "Lightning Investment Holdings Limited",
    "TGuWCuGCrnpVr7aHkB7xAkBMT5Ybce2RwX": "Lightning Investment Holdings Limited",
    "TPrQyYygWTCiY99unm9ekvjwJMxgpUedRA": "K&L Capital Limited",
    "TKtwjYPNn6FFWhnEvsisoQ5TKj4Pgjwgum": "Li Canal Holdings Limited",
    "TPhGmczy3wkUGafFT8QMXPLN2rzdxeChME": "GLOBAL SONIC LIMITED",
    "TFWcZ7UYsfynpCc6xipMwxiEqBSm7uf7y9": "HuobiPay UAB",
    "0xDBF5E9c5206d0dB70a90108bf936DA60221dC080": "Wintermute Trading LTD"
}

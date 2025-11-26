# Users-2FA-Login
Run the scripts on Ubuntu  
Document:https://sonicwall.atlassian.net/wiki/spaces/SQA/pages/1405648917/How+to+do+Users+2FA+Login+test

# SSLVPN Automation Test Suite

## 📋 Project Overview

This project contains a series of automated test cases for SSLVPN functionality, designed to continuously test firewall SSL VPN portal and NetExtender client login operations.

## 🧪 Test Cases

### 1. SSLVPN Portal Login Test

#### Test Name
`SSLVPNPortal_Login_With_Correct_OTPCode`

#### Description
This test case is designed to continuously test the SSLVPN portal by performing repeated login and logout operations.

#### Test Steps
1. **Cleanup Phase**
   - Delete mapping files and OTP code storage files
   - Remove all virtual network interfaces under ens192

2. **Preparation Phase**
   - Add virtual network interfaces
   - Create mapping files associating each user with corresponding virtual interface IP addresses

3. **Execution Phase**
   - Perform user login and 2FA authentication
   - Perform user logout
   - Repeat the entire process

#### Topology
```
Firewall interface(WAN) -- Ubuntu(ens192)
```

#### Script Structure
```
Users_2FA_Login/
├── SSLVPNPortal_Login_With_Correct_OTPCode/
│   └── config_data.py
└── SMTP_Server.py
```

---

### 2. SSL VPN NetExtender Login Test

#### Test Name
`SSLVPN_NX_Login_With_Correct_OTPCode`

#### Description
This test case is designed to continuously test the SSLVPN NetExtender by performing repeated login and logout operations.

#### Test Steps
1. **Cleanup Phase**
   - Delete mapping files and OTP code storage files

2. **Execution Phase**
   - Perform user login and 2FA authentication
   - Execute expect file for NetExtender connection
   - Perform user logout
   - Repeat the entire process

#### Topology
```
Firewall interface(X1) -- Ubuntu(ens160)
```

#### Script Structure
```
Users_2FA_Login/
├── SSLVPN_NX_Login_With_Correct_OTPCode/
│   └── nx_data.py
└── SMTP_Server.py
```

---

### 3. Distributed SMTP Server Configuration

#### Description
This case design involves deploying the SMTP server and the 2FA login scripts on two separate Ubuntu systems.

#### Deployment Architecture

**Ubuntu A (SMTP Server)**
- Run `API_SMTP_Server.py`

**Ubuntu B (Test Client)**
- Run `API_Server_OTPCode.py`
- Run 2FA login test scripts

#### Execution Flow
1. Start `API_SMTP_Server.py` on Ubuntu A
2. Start `API_Server_OTPCode.py` on Ubuntu B
3. Execute 2FA login test scripts on Ubuntu B

#### Script Structure
```
Ubuntu A:
└── API_SMTP_Server.py

Ubuntu B:
Users_2FA_Login/
├── SSLVPNPortal_Login_With_Correct_OTPCode/
│   └── config_data.py
└── API_Server_OTPCode.py
```

## ⚠️ Important Notes

- **File Paths**: Pay special attention to file path configurations in scripts
- **Network Configuration**: Ensure virtual network interfaces are properly configured
- **Dependencies**: SMTP server must be started before test scripts

## 🚀 Quick Start

1. Configure network topology environment
2. Deploy SMTP server (Ubuntu A)
3. Configure test client (Ubuntu B)
4. Execute relevant test cases as needed

## 📁 Project Structure

```
SSL-VPN-Automation-Tests/
├── README.md
├── SSLVPNPortal_Login_With_Correct_OTPCode/
│   ├── config_data.py
│   └── README_PORTAL.md
├── SSLVPN_NX_Login_With_Correct_OTPCode/
│   ├── nx_data.py
│   └── README_NX.md
├── SMTP_Server.py
└── API_Server_OTPCode.py
```

## 🔧 Prerequisites

- Ubuntu systems with network configuration access
- Python environment
- Firewall with SSL VPN configured
- Network connectivity between test components

Would you like me to add any specific technical details or usage instructions for any of the test cases?

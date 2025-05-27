This project is a **simulated ransomware** program built for **educational**, **research**, and **testing** purposes only.  
It demonstrates basic concepts of file encryption, timers, and decryption mechanisms in a controlled environment.

---

# ⚠️ Disclaimer

> **Educational Purposes Only**  
>  
> This project is intended solely for educational, research, and cybersecurity training purposes.  
>  
> - **I do not condone** the use of this project for malicious, illegal, or harmful activities.
> - **I am not responsible** for any damages, legal consequences, or misuse of this code.
> - **You are fully responsible** for how you use this information and code.
> - **Only use it** inside isolated environments such as Virtual Machines (VMs) or test sandboxes.
> - **This project will not function outside a Virtual Machine (VM).**  
>   It has been designed **exclusively** for testing in isolated environments. If run outside a VM, the program will exit without performing any actions.

> By cloning, downloading, or using this project, you agree to use it responsibly and legally.

---

# Features

### C2 Features
- **Key Upload & Delivery** - Stores and sends RSA keys to verified clients.
- **JWT Sessions** - Authenticated client sessions with expiration.
- **Mock Payments** - Simulated BTC address and payment tracking.
- **Key Expiry** - Auto-deletes keys after timer ends.
- **Rate Limiting** - Prevents API abuse and flooding.
- **Logging** - Logs all requests and responses in JSON.
- **Access Control** - Requires API key and session token.
- **SQLite DB** - Tracks keys, payments, and timestamps.

### Client Features
- **RSA + AES Encryption** - Encrypts user files with hybrid encryption.
- **Destruction Timer** - Deletes keys or files after countdown expires.
- **Persistence Simulation** - Mimics startup behavior on reboot.
- **C2 Communication** - Interacts with the C2 server for key upload, status checks, and decryption.

---
# Usage

1: Open and edit `c2_server = "http://c2-server-ip:5000"` in `Variables.py` file to what your C2 server ip is.

2: Navigate to `C2` directory and install dependencies on the C2 server.
```
pip install -r C2_requirements.txt
```

3: Run the C2 server using `C2.py`
```
python3 C2.py
```

4: Navigate to `Client` directory and install dependencies on the target VM
```
pip install -r requirements.txt
```

5: Run `Main.py` on the target VM
```
python3 Main.py
```
6: Open your browser and go to: `http://c2-server-ip:5000/dashboard/home` to view logs and other dashboard info.


---

# 📜 Final Legal Notice

 This project was developed **solely for educational, research, and cybersecurity awareness purposes**.
 It is intended for use in **controlled environments** such as test networks, virtual machines (VMs), and educational labs.

 By cloning, downloading, viewing, or using this project in any way, you acknowledge and agree that:
 - You are fully responsible for your actions.
 - You will use this project **legally and ethically**.
 - You will **not** use this project for unauthorized access, disruption, damage, or harm to others' systems, networks, or data.
 - You understand that **misuse may be illegal** under local, national, or international laws.

 The creator of this project **do not condone**, **support**, or **encourage** any malicious, unethical, or illegal behavior.
 **The creator hold no responsibility or liability** for any misuse, damage, loss, or legal consequences resulting from the use of this code.

 This project exists **to promote understanding** of ransomware techniques so that cybersecurity professionals can better detect, prevent, and respond to real-world threats.

 ⚠️ **Use responsibly. Stay ethical. Stay legal.**

---

### MIT License with Educational Use and Controlled Environment Clause
Copyright (c) 2024 [BBlue530]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software under the following conditions:
Educational Use Only:
This software is intended for educational, research, and cybersecurity training purposes only. It must be used within controlled, isolated environments, such as virtual machines (VMs) or sandboxes, that are completely isolated from production or live systems. Any use outside such environments is prohibited.

No Commercial Use:
The software may not be used for any commercial purposes, including but not limited to selling, licensing, or using in any commercial product or service.

Restricted Distribution:
You may not distribute this software or any modified versions of it in a way that encourages, supports, or enables malicious, illegal, or unauthorized use.

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


---

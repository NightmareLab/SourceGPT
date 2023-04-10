
----

## smartcontract_vuln.py_tests
 - Topics: web3 smart contract vulnerabilities
 - Testing smartcontract_vuln.py prompt model
 - Prompt inspired by https://github.com/SunWeb3Sec/DeFiVulnLabs

### MyBank.zip

 - It does contain an integer overflow
 - As can be seen from the output we have found the vuln and also some false positives
 - We can ask more selective question, e.g. to find where's the code location of such vuln, or write a prompt per vulnerability should be the best option
 - Example of output:
```
 1. Integer Overflow 1 | Integer Overflow 2: The use of unsigned integers without a SafeMath library may result in an integer overflow or underflow, leading to unexpected behavior or a potential loss of funds. 2. Selfdestruct 1 | Selfdestruct 2: The lack of access control on the selfdestruct() function may allow malicious parties to delete the contract and steal any Ether stored in it. 3. Unsafe Delegatecall: Unsafe delegatecall operations may allow
```

<br />

----

## capa_minimal.py_tests
 - Topics: malware analysis
 - Testing capa_minimal.py prompt model
 - Prompt inspired by https://github.com/fireeye/capa/

### NormalProgramTrustMe.zip 
 - UAC bypass
 - As noted from the output, chatgpt does consider it as an exploit rather than a malware, maybe my definition is not strong enough, besides it gives some capabilities of the program
 - Example of output:
```
Malware Score: 0/100 Exploit Score: 100/100 The code in the file appears to be an exploit for bypassing UAC using Event Viewer. It contains a registry entry that is used to execute a command (default is "C:\Windows\System32\colorcpl.exe") and a thread that runs "C:\Windows\System32\eventvwr.msc". The code also contains code for reading and writing files, resolving DNS
```

<br />

----

## rce_taint_analysis.py_tests
 - Topics: vulnerability research
 - Testing rce_taint_analysis.py prompt model
 - Scenario: We have this ELF binary that we decompiled by ghidra

### Env.zip 
 - The source code was extracted with ghidra and ghidra2dwarf plugin
 - Example of output:
```
 Yes, I can confirm that the user input is used inside the system-alike libc library functions. Specifically, it is taken by the 'getenv' libc library function. I can also confirm that a taint analysis can be done in order to help with the analysis.
```


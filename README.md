# Ursina for Mobile CLI utility
This utility lets you build, create and install more easily UfM (Ursina for Mobile) projects. 

## Requirements: 
For now, because UfMCLI is in beta, it's not available in PyPi. Here are the requirements 
- Having this repository cloned (`git clone https://github.com/PaologGithub/ufmcli`)
- Having any capable python project handler, `uv` is recommended.
- Having Python **3.13**. **WARNING:** only 3.13 is supported.
- Having Java >=11

## Commands:
### check
| Arguments        | Description           | Supported             | Default |
|------------------|-----------------------|-----------------------|---------|
| `<project_dir>`  | Project directory     | Any folder path       | `.`     |
| `--java-command` | Java command to use   | Any `java`/`java.exe` | `java`  |

**Goal:** Check the current environment, to see that everything works.

**Examples:**
- `ufmcli check`
- `ufmcli check --java-command C:\Users\Paolog\.jdks\ms-25.0.4.1\bin\java.exe` (checks with a certain java executable)

### build
| Arguments        | Description           | Supported             | Default |
|------------------|-----------------------|-----------------------|---------|
| `<project_dir>`  | Project directory     | Any folder path       | `.`     |
| `--skip-check`   | Skip env check        | Skips if entered      | `False` |
| `--java-command` | Java command to use   | Any `java`/`java.exe` | `java`  |
| `--abi`          | Android ABI to build  | `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`, `all` | `all`  |

**Goal:** Builds the UfM project

**Examples:**
- `ufmcli build`
- `ufmcli build C:\Users\Paolog\Documents\UrsinaForMobile` (build a certain project path)
- `ufmcli build --java-command C:\Users\Paolog\.jdks\ms-25.0.4.1\bin\java.exe` (build with a certain java executable)
- `ufmcli build --abi arm64-v8a` (build only for arm 64bit)

### install
| Arguments        | Description           | Supported             | Default |
|------------------|-----------------------|-----------------------|---------|
| `<project_dir>`  | Project directory     | Any folder path       | `.`     |
| `--java-command` | Java command to use   | Any `java`/`java.exe` | `java`  |

**Goal:** Install the application. You need a device connected to ADB

**Examples:**
- `ufmcli install`
- `ufmcli install --java-command C:\Users\Paolog\.jdks\ms-25.0.4.1\bin\java.exe` (installs with a certain java executable)
# MetadataFS - A Virtual Filesystem with Extended Attributes (xattrs)

**MetadataFS** is a simple in-memory filesystem built with [fusepy](https://github.com/fusepy/fusepy) that supports **extended attributes (xattrs)**. This allows you to store metadata like categories, tags, or custom flags independently of the file content. It's an excellent tool for learning how filesystems work at a low level.

---

## 🚀 Features

- **In-Memory Storage**: All files and metadata exist only in RAM and are lost when unmounted.
- **Standard File Operations**: Supports creating, reading, writing, and deleting files.
- **Extended Attributes (xattrs)**: Attach custom metadata (tags, categories) to any file or directory.
- **Verbose Logging**: See every filesystem operation happening in the terminal as you interact with it.
- **Standard Tool Integration**: Works seamlessly with Linux commands like `ls`, `cat`, `rm`, `touch`, `getfattr`, and `setfattr`.

---

## 🔧 How to Use

### 1. Install Dependencies

Make sure you have `fusepy` and the `attr` command-line tools installed:

```bash
# Install the Python library
pip install fusepy

# Install command-line tools for xattrs (Debian/Ubuntu)
sudo apt install attr
```

### 2. Save the Script

Save the filesystem code to a file named `metadata_fs.py`.

### 3. Create a Mount Point

This is the empty directory where your virtual filesystem will appear:

```bash
mkdir ~/meta_fs
```

### 4. Run the Filesystem

In a terminal, run the script and provide the mount point:

```bash
python metadata_fs.py ~/meta_fs
```

> ⚠️ Keep this terminal open! It will display live logs of all operations. You will interact with the filesystem from a second terminal.

---

## 🧾 Usage Examples

Open a **second terminal** and try the following commands. Watch the logs in the first terminal to see which Python methods are being called!

### Standard File & Directory Operations

#### **List Files and Directories**
See what's inside your filesystem.
```bash
# List only the file names
ls ~/meta_fs

# List with detailed attributes (permissions, size, owner, etc.)
ls -l ~/meta_fs
```
*__How it works:__ These commands trigger the `readdir` and `getattr` methods in your script.*

#### **Create a File**
You can create an empty file or a file with content.
```bash
# Create a new, empty file
touch ~/meta_fs/my_empty_file.log

# Create a file and write content to it in one step
echo "Hello FUSE World!" > ~/meta_fs/hello.txt
```
*__How it works:__ `touch` triggers `create`. `echo >` triggers `create`, `open`, `truncate`, and `write`.*

#### **Read File Content**
View the content you just wrote.
```bash
cat ~/meta_fs/hello.txt
```
*__How it works:__ This triggers the `open` and `read` methods.*

#### **Delete a File**
Remove a file from the filesystem.
```bash
rm ~/meta_fs/hello.txt
```
*__How it works:__ This triggers the `unlink` method.*

### Extended Attribute (xattr) Operations

This filesystem also supports custom metadata on any file. Let's use the pre-created `exemplo.txt`.

#### **List All xattrs of `exemplo.txt`**
```bash
getfattr -d ~/meta_fs/exemplo.txt
```
**Expected output:**
```ini
# file: /home/youruser/meta_fs/exemplo.txt
user.category="documents"
user.classification="important"
user.tags="sample,python"
```
*__How it works:__ This triggers `listxattr` and `getxattr` for each attribute.*

#### **Read a Specific Attribute**
```bash
getfattr -n user.category ~/meta_fs/exemplo.txt
```
*__How it works:__ This triggers the `getxattr` method.*

#### **Set or Update an Attribute**
```bash
setfattr -n user.author -v "Gemini" ~/meta_fs/exemplo.txt
```
*__How it works:__ This triggers the `setxattr` method.*

#### **Remove an Attribute**
```bash
setfattr -x user.tags ~/meta_fs/exemplo.txt
```
*__How it works:__ This triggers the `removexattr` method.*

---

## 🧹 Unmount and Clean Up

When you're finished, stop the Python script with `Ctrl+C` in the first terminal, and then unmount the filesystem:

```bash
fusermount -u ~/meta_fs
```

---

## 📎 Notes

- `exemplo.txt` is pre-created with some example xattrs to get you started.
- For security, the code avoids using `allow_other=True`. This means only your user can access the mounted filesystem.


# MetadataFS - A Virtual Filesystem with Extended Attributes (xattrs)

**MetadataFS** is a simple in-memory filesystem built with [fusepy](https://github.com/fusepy/fusepy) that supports **extended attributes (xattrs)**. This allows you to store metadata like categories, tags, or custom flags independently of the file content.

---

## 🚀 Features

- Create and read files from a virtual filesystem.
- Support for custom metadata (xattrs) per file or directory.
- Integration with standard Linux tools like `getfattr` and `setfattr`.
- In-memory storage (no data persisted to disk).

---

## 📚 What Are Extended Attributes (xattrs)?

Extended attributes are like "tags" or extra fields you can attach to files. They are not part of the file content but store additional metadata.

By convention, user-defined attributes use the `user.` prefix:

```bash
user.category="documents"
user.tags="python,fuse,tutorial"
user.classification="important"
```

These attributes can be manipulated with tools like `getfattr` and `setfattr`.

---

## 🔧 How to Use

### 1. Install Dependencies

Make sure you have `fusepy` and attribute tools installed:

```bash
pip install fusepy
sudo apt install attr   # For getfattr and setfattr
```

### 2. Save the Script

Save the filesystem code to a file named:

```bash
metadata_fs.py
```

### 3. Create a Mount Point

This is the directory where the virtual filesystem will be mounted:

```bash
mkdir ~/meta_fs
```

### 4. Run the Filesystem

In a terminal, run:

```bash
python metadata_fs.py ~/meta_fs
```

> ⚠️ Keep this terminal open while interacting with the filesystem.

---

## 🧾 Usage Examples

Open a second terminal and try the following examples:

### 📄 List All xattrs of `exemplo.txt`

```bash
getfattr -d ~/meta_fs/exemplo.txt
```

**Expected output:**

```ini
# file: /home/youruser/meta_fs/exemplo.txt
user.category="documents"
user.classification="important"
user.tags="example,python"
```

### 🔍 Read a Specific Attribute

```bash
getfattr -n user.category ~/meta_fs/exemplo.txt
```

### 🏷️ Set a New Attribute

```bash
setfattr -n user.author -v "Gemini" ~/meta_fs/exemplo.txt
```

### ✅ Check the New Attribute

```bash
getfattr -n user.author ~/meta_fs/exemplo.txt
```

### ❌ Remove an Attribute

```bash
setfattr -x user.tags ~/meta_fs/exemplo.txt
```

---

## 🧹 Unmount and Clean Up

When you're done, unmount the filesystem:

```bash
fusermount -u ~/meta_fs
```

---

## 📎 Notes

- All files and attributes exist only **in memory** — they are lost once the filesystem is unmounted.
- `exemplo.txt` is **pre-created** with some example xattrs.
- For security, avoid using `allow_other=True` unless necessary.

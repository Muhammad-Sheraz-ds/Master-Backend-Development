## S3 Concept 1: Buckets and Objects

### 1. Bucket

A **bucket** is the main storage container in S3.

Think:

```text
Bucket = big box
```

Example:

```text
my-app-uploads
company-documents
user-profile-images
```

You store files inside a bucket.

---

### 2. Object

An **object** is the actual file stored in S3.

Think:

```text
Object = file inside the box
```

Example objects:

```text
profile.png
invoice.pdf
video.mp4
resume.docx
```

---

### 3. Key

Every object has a **key**.

The key is the full name/path of the file inside the bucket.

Example:

```text
users/101/profile.png
invoices/2025/january/invoice-1.pdf
videos/course/lesson-1.mp4
```

Important: S3 does **not** have real folders.
It only uses keys that look like folders.

---

### 4. Bucket + Key = File Location

To find a file in S3, you need:

```text
bucket name + object key
```

Example:

```text
Bucket: my-app-uploads
Key: users/101/profile.png
```

Together, this identifies one file.

---

### 5. Object contains more than just file data

An S3 object has:

```text
file content
key
metadata
size
content-type
last modified date
permissions
version id, if versioning is enabled
```

Example:

```text
Key: users/101/profile.png
Content-Type: image/png
Size: 240 KB
```

---

### 6. Bucket names must be unique

Bucket names are globally unique.

So this may fail:

```text
my-bucket
```

because someone else may already have it.

Better:

```text
mycompany-prod-user-uploads
```

---

### 7. Common bucket structure

Example:

```text
my-app-files
  users/101/profile.png
  users/102/profile.png
  invoices/2025/invoice-1.pdf
  reports/monthly/report.csv
```

Again, these are not real folders. They are object keys.

---

### 8. Simple summary

```text
Bucket = container
Object = file
Key = file path/name
```

Example:

```text
Bucket: my-app-files
Object Key: users/101/avatar.png
Object Content: the actual image
```

Learn this clearly first. This is the foundation of S3.




# S3 Concept 2: Regions

### What is a Region?

A **Region** is the physical location where your bucket is created.

Examples:

```text
us-east-1     -> Virginia (USA)
us-west-2     -> Oregon (USA)
eu-west-1     -> Ireland
ap-south-1    -> Mumbai
```

---

### Why Regions Matter

#### 1. Latency (Speed)

If your users are in India:

```text
ap-south-1 (Mumbai)
```

will usually be faster than:

```text
us-east-1 (Virginia)
```

because data travels a shorter distance.

---

#### 2. Cost

Data transfer costs can vary between regions.

Different regions may have slightly different pricing.

---

#### 3. Compliance

Some companies must keep data in a specific country or region.

Example:

```text
European customer data
→ stored in EU region
```

---

### Bucket Belongs to One Region

When you create a bucket:

```text
my-app-files
```

you choose:

```text
Region = ap-south-1
```

That bucket lives there.

---

### Example

```text
Bucket:
  my-app-files

Region:
  ap-south-1

Objects:
  users/101/profile.png
  invoices/1.pdf
```

All these objects are stored in the Mumbai region.

---

### Interview-Level Points

Know these:

✅ Every bucket is created in a region

✅ Region affects latency and cost

✅ Choose region close to users

✅ Bucket cannot exist in multiple regions by default

✅ Bucket name is globally unique across all regions

---

### Tiny Summary

```text
Region = where AWS physically stores your bucket.
```

Once you're comfortable with this, the next important concept is:

```text
S3 Access Control
(IAM, Bucket Policies, Public vs Private)
```

That's where most real-world S3 interview questions start.

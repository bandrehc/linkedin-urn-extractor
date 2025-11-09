# LinkedIn URN Scraper v2

Production scraper for extracting URNs from LinkedIn companies and people profiles.

## What Works

**For Companies:**
- ✅ Company URN (`urn:li:fsd_company:12345`)
- ✅ Company ID (numeric)
- ✅ Company Name
- ✅ Follower Count

**For People:**
- ✅ Person URN (`urn:li:fsd_profile:xxxxx` or `urn:li:member:12345`)
- ✅ Person ID
- ✅ Full Name
- ✅ Headline (job title)
- ✅ Connection Count

---

## Requirements

```bash
pip install requests beautifulsoup4 lxml
```

---

## Usage

### Setup
```bash
echo "YOUR_LI_AT_COOKIE" > cookie.txt
```

### Single URL
```bash
# Company
python urnScraper.py --cookie-file cookie.txt https://www.linkedin.com/company/tesla/

# Person
python urnScraper.py --cookie-file cookie.txt https://www.linkedin.com/in/satya-nadella/
```

### Batch Processing
```bash
python urnScraper.py --cookie-file cookie.txt -i urls.txt -o results.csv
```

### Input File Format
```
https://www.linkedin.com/company/microsoft/
https://www.linkedin.com/company/google/
https://www.linkedin.com/in/satya-nadella/
https://www.linkedin.com/in/sundar-pichai/
```

---

## Output Schema

### CSV Columns
- `input_url` - Original URL
- `entity_type` - "company" or "person"
- `urn` - Full URN identifier
- `entity_id` - Numeric/alphanumeric ID
- `name` - Company name or person full name
- `followers` - Follower/connection count
- `headline` - Job title (people only)

### Example Output
```csv
input_url,entity_type,urn,entity_id,name,followers,headline
https://www.linkedin.com/company/microsoft/,company,urn:li:fsd_company:1035,1035,Microsoft,20000000,
https://www.linkedin.com/in/satya-nadella/,person,urn:li:fsd_profile:satyanadella,satyanadella,Satya Nadella,12500000,Chairman and CEO at Microsoft
```

---

## Person URN Patterns

1. **Profile URN:** `urn:li:fsd_profile:username` (most common)
2. **Member URN:** `urn:li:member:12345` (numeric ID)

The scraper extracts whichever is available.

---

## Command Options

```
python urnScraper.py [options]

Required:
  --cookie VALUE              LinkedIn li_at cookie value
  --cookie-file FILE          File containing cookie (recommended)

Input/Output:
  url                         Single URL (company or person)
  -i, --input FILE           Input file with URLs
  -o, --output FILE          Output CSV (default: output.csv)

Rate Limiting:
  --delay-min SECONDS        Min delay (default: 2)
  --delay-max SECONDS        Max delay (default: 5)

Help:
  --help                     Show usage
  --help-cookie              Show cookie instructions
```

---

## Rate Limiting

- Default: 2-5 second delays
- Recommended for 50-200 URLs: 3-6 seconds
- Large batches: Split into 50-URL chunks with pauses

---

## Error Handling

```
HTTP 999           → Rate limited, increase delays
Auth wall          → Cookie invalid, refresh
No URN found       → Invalid URL or blocked page
Empty name field   → JSON parsing failed, URN still valid
```

---

## Use Cases

**Primary:** URN extraction for API operations
**Not Suitable For:** Comprehensive company/person data collection

## About the cookie

**Duration:** ~1 year  
**Invalidated By:** Password change, explicit logout  
**Renewal:** Extract new cookie when auth errors occur  

---

## Support

```bash
python urnScraper.py --help
python urnScraper.py --help-cookie
```

---

## License

For Ventures AI use only.
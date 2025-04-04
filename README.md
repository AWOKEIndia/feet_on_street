# Feet on Street - Frappe Module  

**A Frappe/ERPNext module for geospatial survey data collection.**  

---

## 📖 Overview  
This Frappe app extends **ERPNext/Frappe HR** with: 
- Geographic hierarchy management  
- GPS-tagged survey data collection with automated reporting  

---

## ✨ Features
### **Survey System**  
🌐 Custom geographic hierarchy (State → Region → District → Block → Village)  
📸 Geo-tagged image uploads with automatic GPS coordinate extraction  
📍 Auto-mapping of photos to geographic hierarchy levels  
📝 Customizable survey forms with participant tracking  
🖨️ PDF report generation (sessions, outcomes)  

### **Core HR Features**  (Subject to change)
✅ Employee CheckIns with location validation  
✅ Attendance request workflows  
✅ Leave management with balance tracking  
✅ Expense claim submission with receipt upload  

---

## 🛠️ Prerequisites  
- Frappe/ERPNext v15+  
- Python 3.11+  
- MariaDB  
- Redis (for background jobs)  

---

## 🚀 Installation  

1. Add to your bench:  
```bash
bench get-app https://github.com/AWOKEIndia/feet_on_street.git
```

2. Install on site:  
```bash
bench --site yoursite.com install-app feet_on_street
```

3. Set up required dependencies:  
```bash
bench setup requirements
```

---

## ⚙️ Configuration  

### **1. Geographic Hierarchy Setup**  
Navigate to:  
`Feet on Street > Geographic Settings`  

1. Import pre-defined locations via CSV  
2. Configure hierarchy levels (State → Region → District → etc.)  
3. Assign employees to geographic units  

### **2. Image Processing**  
Enable/disable in `hooks.py`:  
```python
# Enable GPS extraction from images
ENABLE_GPS_EXTRACTION = True

# Enable image quality validation 
VALIDATE_IMAGES = True
```

### **3. API Security**  (Subject to change)
Configure in `site_config.json`:  
```json
{
  "rate_limit": {
    "survey_api": "50/hour"
  }
}
```

---

## 📚 Documentation  

### **Doctypes**  (Subject to change)
| Name | Purpose |  
|------|---------|  
| `Survey Session` | Core survey data collection |  
| `Geographic Unit` | Hierarchy management |  
| `Employee CheckIn` | Location-tagged checkins |  

### **API Endpoints**  (Subject to change)
All endpoints require JWT authentication:  

| Endpoint | Method | Description |  
|----------|--------|-------------|  
| `/api/method/feet_on_street.api.submit_checkin` | POST | Submit employee check-in |  
| `/api/method/feet_on_street.api.create_session` | POST | Create survey session |  
| `/api/method/feet_on_street.api/get_location_hierarchy` | GET | Fetch geographic tree |  

**Example CURL**:  
```bash
curl -X POST \
  -H "Authorization: token <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"employee":"EMP001", "lat":28.4595, "lng":77.0266}' \
  https://yoursite.com/api/method/feet_on_street.api.submit_checkin
```

---

## 🧑💻 Development  

### **Customizing Survey Forms**  
1. Edit `survey_session.json` in `/feet_on_street/doctype/survey_session/`  
2. Add custom fields as needed  

### **Adding New Report Types**  
1. Create new Jinja template in `/feet_on_street/report_templates/`  
2. Register report in `report.py`  

---

## 📜 License  
MIT  

---

## 📞 Support  
**Issues**: [GitHub Issues](https://github.com/your-repo/issues)
```


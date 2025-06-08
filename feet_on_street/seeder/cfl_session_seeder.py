#!/usr/bin/env python3
"""
CFL Session Data Seeder for Feet On Street Module
Creates fake CFL Session records using existing hierarchical data
"""

import io
import json
import os
import random
import tempfile
from datetime import datetime, timedelta
import traceback

import frappe
import requests
from frappe.utils import add_days, get_datetime, today
from PIL import Image


class CFLSessionSeeder:
    def __init__(self):
        self.villages = []
        self.existing_sessions = []
        self.fake_feedback_templates = [
            "Excellent session! Participants were very engaged and asked great questions.",
            "Good participation from the community. Need to focus more on practical examples.",
            "Session went well. Some participants had difficulty understanding complex concepts.",
            "Very interactive session. Participants shared their own experiences.",
            "Need more visual aids for better understanding. Overall positive response.",
            "Great enthusiasm from participants. They requested follow-up sessions.",
            "Session was informative. Participants appreciated the practical approach.",
            "Good attendance despite weather concerns. Community leaders were supportive.",
            "Participants were initially hesitant but became more engaged as session progressed.",
            "Excellent questions from participants. They showed genuine interest in learning."
        ]

    def load_existing_data(self):
        """Load existing villages and related data"""
        print("Loading existing data...")

        self.villages = frappe.db.sql("""
            SELECT 
                v.name as village_id,
                v.village_name,
                v.block,
                b.block_name,
                b.cfl_center,
                c.name as cfl_center,
                c.center_name,
                c.district,
                d.district_name,
                d.region,
                r.region_name,
                r.company,
                r.state
            FROM `tabVillage` v
            LEFT JOIN `tabBlock` b ON v.block = b.name
            LEFT JOIN `tabCFL Center` c ON b.cfl_center = c.name
            LEFT JOIN `tabDistrict` d ON c.district = d.name
            LEFT JOIN `tabRegion` r ON d.region = r.name
            WHERE v.village_name IS NOT NULL
        """, as_dict=True)

        print(f"Found {len(self.villages)} villages with complete hierarchy")

        existing = frappe.db.sql("""
            SELECT village, COUNT(*) as count 
            FROM `tabCFL Session` 
            GROUP BY village
        """, as_dict=True)

        self.existing_sessions = {item['village']: item['count'] for item in existing}
        print(f"Found existing sessions in {len(self.existing_sessions)} villages")

    def generate_gps_coordinates(self, base_lat=None, base_lng=None):
        if base_lat and base_lng:
            lat_offset = random.uniform(-0.45, 0.45)
            lng_offset = random.uniform(-0.45, 0.45)
            lat = base_lat + lat_offset
            lng = base_lng + lng_offset
        else:
            lat = random.uniform(8.4, 37.6)
            lng = random.uniform(68.7, 97.25)

        return round(lat, 6), round(lng, 6)

    def generate_participant_data(self):
        total_participants = random.randint(15, 80)
        female_ratio = random.uniform(0.45, 0.70)
        females = int(total_participants * female_ratio)
        males = total_participants - females
        head_count = total_participants + random.randint(-3, 5)
        head_count = max(head_count, total_participants)

        return {
            'participants': total_participants,
            'males': males,
            'females': females,
            'head_count': head_count
        }

    def create_placeholder_image(self, image_type="session"):
        try:
            width, height = 800, 600
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            img = Image.new('RGB', (width, height), color=color)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG')
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Could not create placeholder image: {e}")
            return None

    def attach_placeholder_images(self, session_doc):
        try:
            image_fields = [
                'session_image_1', 'session_image_2', 'session_image_3', 'session_image_4',
                'participant_list_image_1', 'participant_list_image_2', 'participant_list_image_3'
            ]

            for i, field in enumerate(image_fields):
                if field in ['session_image_3', 'session_image_4', 'participant_list_image_2', 'participant_list_image_3']:
                    if random.random() < 0.6:
                        continue

                temp_image = self.create_placeholder_image()
                if temp_image:
                    try:
                        file_doc = frappe.get_doc({
                            "doctype": "File",
                            "file_name": f"fake_{field}_{session_doc.name}_{i}.jpg",
                            "is_private": 1,
                            "content": open(temp_image, 'rb').read()
                        })
                        file_doc.save()
                        session_doc.set(field, file_doc.file_url)
                        os.unlink(temp_image)
                    except Exception as e:
                        print(f"Could not attach image {field}: {e}")
                        os.unlink(temp_image)
        except Exception as e:
            print(f"Error in image attachment: {e}")

    def generate_session_date(self, days_back_max=90):
        days_back = random.randint(1, days_back_max)
        return add_days(today(), -days_back)

    def create_fake_session(self, village_data, session_count=1):
        """Create fake session with comprehensive error handling"""
        sessions_created = []
        
        for i in range(session_count):
            session_doc = None
            try:
                participant_data = self.generate_participant_data()
                lat, lng = self.generate_gps_coordinates()
                
                # Create GPS data in correct format for Geolocation field
                gps_data = {
                    "type": "FeatureCollection",
                    "features": [
                        {
                            "type": "Feature",
                            "properties": {},
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lng, lat]
                            }
                        }
                    ]
                }

                # Validate required village data
                if not village_data.get('village_id'):
                    raise ValueError("Village ID is missing")

                # Create required images first
                required_images = {}
                required_fields = ['session_image_1', 'session_image_2', 'participant_list_image_1']
                
                for field in required_fields:
                    temp_image_path = self.create_placeholder_image()
                    if not temp_image_path:
                        raise Exception(f"Could not create required image for {field}")
                    
                    try:
                        with open(temp_image_path, 'rb') as img_file:
                            file_content = img_file.read()
                        
                        # Create unique filename
                        filename = f"fake_{field}_{random.randint(10000, 99999)}.jpg"
                        
                        file_doc = frappe.get_doc({
                            "doctype": "File",
                            "file_name": filename,
                            "is_private": 1,
                            "content": file_content
                        })
                        file_doc.insert(ignore_permissions=True)
                        
                        required_images[field] = file_doc.file_url
                        print(f"  Created required image: {field}")
                        
                    except Exception as e:
                        raise Exception(f"Failed to create required image {field}: {str(e)}")
                    
                    finally:
                        # Clean up temp file
                        try:
                            if os.path.exists(temp_image_path):
                                os.unlink(temp_image_path)
                        except:
                            pass

                session_doc = frappe.get_doc({
                    "doctype": "CFL Session",
                    "village": village_data.village_id,
                    "block": village_data.get('block'),
                    "cfl_center": village_data.get('cfl_center_id'),
                    "district": village_data.get('district'),
                    "region": village_data.get('region'),
                    "company": village_data.get('company'),
                    "participants": participant_data['participants'],
                    "males": participant_data['males'],
                    "females": participant_data['females'],
                    "head_count": participant_data['head_count'],
                    "feedback": random.choice(self.fake_feedback_templates),
                    "gps_location": json.dumps(gps_data),
                    # Add required images
                    "session_image_1": required_images['session_image_1'],
                    "session_image_2": required_images['session_image_2'],
                    "participant_list_image_1": required_images['participant_list_image_1']
                })

                # Insert with required fields populated
                session_doc.insert(ignore_permissions=True)
                print(f"  Created session document: {session_doc.name}")
                
                # Attach optional images
                self.attach_optional_images(session_doc)
                
                # Save with optional images
                session_doc.save(ignore_permissions=True)
                frappe.db.commit()
                
                sessions_created.append(session_doc.name)
                print(f"✓ Successfully created session {session_doc.name} for village {village_data.village_name}")
                
            except Exception as e:
                print(f"✗ Failed to create session for village {village_data.get('village_name', 'Unknown')}: {str(e)}")
                print(f"Stack trace: {traceback.format_exc()}")
                
                # Clean up failed session
                if session_doc and hasattr(session_doc, 'name') and session_doc.name:
                    try:
                        frappe.delete_doc("CFL Session", session_doc.name, ignore_permissions=True)
                        frappe.db.commit()
                    except:
                        pass
                
                continue
                
        return sessions_created

    def attach_optional_images(self, session_doc):
        """Attach optional images only"""
        try:
            optional_fields = [
                'session_image_3', 'session_image_4',
                'participant_list_image_2', 'participant_list_image_3'
            ]
            
            for field in optional_fields:
                # Skip optional fields randomly
                if random.random() < 0.6:
                    continue

                temp_image_path = self.create_placeholder_image()
                if not temp_image_path:
                    continue

                try:
                    with open(temp_image_path, 'rb') as img_file:
                        file_content = img_file.read()
                    
                    # Create unique filename
                    filename = f"fake_{field}_{session_doc.name}_{random.randint(1000, 9999)}.jpg"
                    
                    file_doc = frappe.get_doc({
                        "doctype": "File",
                        "file_name": filename,
                        "is_private": 1,
                        "content": file_content
                    })
                    file_doc.insert(ignore_permissions=True)
                    
                    session_doc.set(field, file_doc.file_url)
                    print(f"  Attached optional image: {field}")
                    
                except Exception as e:
                    print(f"Warning: Could not attach optional image {field}: {str(e)}")
                
                finally:
                    # Clean up temp file
                    try:
                        if os.path.exists(temp_image_path):
                            os.unlink(temp_image_path)
                    except:
                        pass

        except Exception as e:
            print(f"Error in optional image attachment: {str(e)}")

    def seed_sessions(self, max_sessions_per_village=3, total_sessions_limit=100):
        if not self.villages:
            print("No villages found! Please ensure geographic hierarchy is set up.")
            return

        print(f"Starting to seed CFL sessions...")
        print(f"Max sessions per village: {max_sessions_per_village}")
        print(f"Total sessions limit: {total_sessions_limit}")

        sessions_created = []
        total_created = 0

        random.shuffle(self.villages)

        for village in self.villages:
            if total_created >= total_sessions_limit:
                break

            existing_count = self.existing_sessions.get(village.village_id, 0)

            if existing_count == 0:
                session_count = random.randint(1, max_sessions_per_village)
            elif existing_count < max_sessions_per_village:
                if random.random() < 0.3:
                    session_count = random.randint(1, max_sessions_per_village - existing_count)
                else:
                    continue
            else:
                continue

            remaining_slots = total_sessions_limit - total_created
            session_count = min(session_count, remaining_slots)

            if session_count <= 0:
                continue

            created = self.create_fake_session(village, session_count)
            sessions_created.extend(created)
            total_created += len(created)

            print(f"Progress: {total_created}/{total_sessions_limit} sessions created")

        print(f"\n\U0001F389 Seeding completed!")
        print(f"Total sessions created: {len(sessions_created)}")
        print(f"Villages covered: {len(set([s.split('-')[0] for s in sessions_created]))}")

        return sessions_created


def main():
    print("=" * 60)
    print("CFL SESSION DATA SEEDER")
    print("=" * 60)

    seeder = CFLSessionSeeder()
    seeder.load_existing_data()
    if not seeder.villages:
        print("\u274C No villages found in the system!")
        return

    seeder.seed_sessions(max_sessions_per_village=3, total_sessions_limit=100)


if __name__ == '__main__':
    main()

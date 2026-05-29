"""
Seed script - populates the database with sample Guide and Video content.
Run from vet_backend/:
    python -m seeds.seed_content

Content is organised by pet type: cat, dog, rabbit, hamster, guinea_pig.
Each pet type has one guide/video pair for each emergency category:
choking, bleeding, poisoning, fracture, heatstroke.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.guide import Guide
from app.models.user import User
from app.models.video import Video
from app.services.video_hosting import video_hosting


VET_AUTHOR_EMAILS = ("ann.vet@example.com", "ravi.vet@example.com")


def get_author_ids(db):
    vets = (
        db.query(User)
        .filter(User.email.in_(VET_AUTHOR_EMAILS), User.role == "veterinarian")
        .all()
    )
    vet_by_email = {vet.email: vet.userID for vet in vets}
    return [vet_by_email[email] for email in VET_AUTHOR_EMAILS if email in vet_by_email]


def assign_authors(items, author_ids):
    if not author_ids:
        return
    for index, item in enumerate(items):
        item.authorVetID = author_ids[index % len(author_ids)]


def make_guide(title, description, pet_type, emergency_category, steps):
    return Guide(
        title=title,
        description=description,
        petType=pet_type,
        emergencyCategory=emergency_category,
        publicationStatus="published",
        authorVetID=None,
        steps=steps,
        stepCount=len(steps),
    )


def make_video(title, description, pet_type, emergency_category, video_url, duration_sec):
    return Video(
        title=title,
        description=description,
        petType=pet_type,
        emergencyCategory=emergency_category,
        publicationStatus="published",
        authorVetID=None,
        videoURL=video_hosting.getEmbedUrl(video_url) or video_url,
        durationSec=duration_sec,
    )


def seed():
    db = SessionLocal()

    try:
        author_ids = get_author_ids(db)
        guides = [
            make_guide(
                "Cat Choking and Breathing First Aid",
                "Emergency steps if a cat is choking or struggling to breathe.",
                "cat",
                "choking",
                [
                    "Step 1: Stay calm and check whether the cat can cough or breathe.",
                    "Step 2: Look in the mouth only if it is safe and the object is visible.",
                    "Step 3: Remove a visible object gently without pushing it deeper.",
                    "Step 4: Keep the cat calm and do not give food or water.",
                    "Step 5: Contact an emergency vet immediately if breathing does not improve.",
                ],
            ),
            make_guide(
                "How to Stop Bleeding in Cats",
                "Emergency steps to control wounds and bleeding in cats.",
                "cat",
                "bleeding",
                [
                    "Step 1: Restrain the cat gently and keep it as still as possible.",
                    "Step 2: Apply a clean cloth or gauze directly to the wound.",
                    "Step 3: Hold firm pressure for 5-10 minutes without repeatedly checking.",
                    "Step 4: Add more cloth on top if blood soaks through.",
                    "Step 5: Take the cat to a vet immediately for assessment.",
                ],
            ),
            make_guide(
                "Cat Poisoning and Ingestion First Aid",
                "Immediate steps if a cat may have swallowed something toxic.",
                "cat",
                "poisoning",
                [
                    "Step 1: Move the cat away from the suspected poison.",
                    "Step 2: Do not make the cat vomit unless a vet instructs you.",
                    "Step 3: Keep packaging, plant material, or a sample of the substance.",
                    "Step 4: Wipe poison from the mouth or fur with a damp cloth if safe.",
                    "Step 5: Call a vet or emergency clinic immediately.",
                ],
            ),
            make_guide(
                "Cat Fracture and Injury First Aid",
                "How to protect a cat with a suspected fracture, spinal injury, or serious fall.",
                "cat",
                "fracture",
                [
                    "Step 1: Keep the cat still and avoid unnecessary handling.",
                    "Step 2: Do not try to straighten or splint a limb unless told by a vet.",
                    "Step 3: Slide the cat onto a firm towel or board if it must be moved.",
                    "Step 4: Keep the cat warm, quiet, and confined during transport.",
                    "Step 5: Seek emergency veterinary care immediately.",
                ],
            ),
            make_guide(
                "Cat Heatstroke and Shock First Aid",
                "Emergency cooling steps for an overheated or collapsed cat.",
                "cat",
                "heatstroke",
                [
                    "Step 1: Move the cat to a cool, shaded, well-ventilated area.",
                    "Step 2: Apply cool water to the paws, belly, and ears; do not use ice.",
                    "Step 3: Offer small amounts of cool water only if the cat is alert.",
                    "Step 4: Keep the cat calm and watch for weakness, panting, or collapse.",
                    "Step 5: Contact a vet urgently, even if the cat seems to improve.",
                ],
            ),
            make_guide(
                "Dog Choking and Breathing First Aid",
                "What to do if a dog is choking on a foreign object.",
                "dog",
                "choking",
                [
                    "Step 1: Check whether the dog can cough, breathe, or make noise.",
                    "Step 2: Look into the mouth for a visible object.",
                    "Step 3: Remove a visible object carefully with fingers or tweezers.",
                    "Step 4: Use back blows or abdominal thrusts only if the dog cannot breathe.",
                    "Step 5: Go to the vet even if the object is removed.",
                ],
            ),
            make_guide(
                "Dog Wound and Bleeding Control",
                "Emergency steps to control wounds and bleeding in dogs.",
                "dog",
                "bleeding",
                [
                    "Step 1: Keep the dog still and calm.",
                    "Step 2: Apply clean gauze or cloth directly to the wound.",
                    "Step 3: Press firmly for 5-10 minutes without lifting the cloth.",
                    "Step 4: Add another layer if blood soaks through.",
                    "Step 5: Bring the dog to a vet immediately for deep or ongoing bleeding.",
                ],
            ),
            make_guide(
                "Dog Poisoning and Ingestion First Aid",
                "What to do if a dog may have eaten something poisonous.",
                "dog",
                "poisoning",
                [
                    "Step 1: Remove the dog from the source of poison.",
                    "Step 2: Do not force vomiting unless a vet tells you to.",
                    "Step 3: Keep the product label, plant, medication, or food sample.",
                    "Step 4: Watch for drooling, vomiting, shaking, weakness, or collapse.",
                    "Step 5: Call a vet or emergency clinic immediately.",
                ],
            ),
            make_guide(
                "Dog Fracture and Injury First Aid",
                "How to move and protect a dog with a suspected fracture or serious injury.",
                "dog",
                "fracture",
                [
                    "Step 1: Keep the dog calm and prevent walking or running.",
                    "Step 2: Do not attempt to reset a bone or force a limb into position.",
                    "Step 3: Muzzle only if needed and safe, avoiding breathing restriction.",
                    "Step 4: Support the body with a towel, blanket, or firm board for transport.",
                    "Step 5: Seek veterinary care urgently.",
                ],
            ),
            make_guide(
                "Dog Heatstroke and Shock First Aid",
                "Immediate steps for a dog showing signs of heatstroke or shock.",
                "dog",
                "heatstroke",
                [
                    "Step 1: Move the dog to a cool, shaded area immediately.",
                    "Step 2: Wet the body with cool water; do not use ice water.",
                    "Step 3: Place the dog near moving air such as a fan.",
                    "Step 4: Offer small amounts of cool water if the dog is alert.",
                    "Step 5: Contact a vet urgently, even if symptoms improve.",
                ],
            ),
            make_guide(
                "Rabbit Choking and Breathing First Aid",
                "Emergency steps if a rabbit is choking or breathing abnormally.",
                "rabbit",
                "choking",
                [
                    "Step 1: Keep the rabbit calm and avoid stressful handling.",
                    "Step 2: Check for open-mouth breathing, blue gums, weakness, or panic.",
                    "Step 3: Do not place fingers deep in the mouth unless an object is visible.",
                    "Step 4: Keep the rabbit upright and in a quiet space with fresh air.",
                    "Step 5: Seek emergency veterinary care immediately.",
                ],
            ),
            make_guide(
                "Rabbit Wound and Bleeding First Aid",
                "Emergency steps to control wounds and bleeding in rabbits.",
                "rabbit",
                "bleeding",
                [
                    "Step 1: Handle the rabbit gently and support the body.",
                    "Step 2: Apply clean gauze or cloth to the bleeding area.",
                    "Step 3: Use gentle but firm pressure for several minutes.",
                    "Step 4: Keep the rabbit warm, calm, and on clean dry bedding.",
                    "Step 5: Contact a vet if bleeding continues or the wound is deep.",
                ],
            ),
            make_guide(
                "Rabbit Poisoning and Ingestion First Aid",
                "What to do if a rabbit may have eaten something unsafe or toxic.",
                "rabbit",
                "poisoning",
                [
                    "Step 1: Remove the rabbit from the suspected toxin or unsafe food.",
                    "Step 2: Do not try to make the rabbit vomit.",
                    "Step 3: Keep a sample or photo of the plant, food, or chemical.",
                    "Step 4: Offer hay and water only if the rabbit is alert and breathing normally.",
                    "Step 5: Call an exotic-pet vet urgently.",
                ],
            ),
            make_guide(
                "Rabbit Fracture and Injury First Aid",
                "How to protect a rabbit after a fall, suspected fracture, or serious injury.",
                "rabbit",
                "fracture",
                [
                    "Step 1: Keep the rabbit still and avoid lifting by the limbs.",
                    "Step 2: Support the whole body and hindquarters when moving it.",
                    "Step 3: Place the rabbit in a padded carrier with limited space to move.",
                    "Step 4: Do not splint or straighten the injured area at home.",
                    "Step 5: Seek exotic-pet veterinary care immediately.",
                ],
            ),
            make_guide(
                "Rabbit Heatstroke and Shock First Aid",
                "Immediate steps for a rabbit showing signs of overheating or shock.",
                "rabbit",
                "heatstroke",
                [
                    "Step 1: Move the rabbit to a cool, shaded area immediately.",
                    "Step 2: Dampen the ears with cool water; do not soak the rabbit.",
                    "Step 3: Place the rabbit near gentle moving air.",
                    "Step 4: Offer small amounts of cool water if the rabbit is alert.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
            make_guide(
                "Hamster Breathing Difficulty First Aid",
                "Emergency steps if a hamster is choking or breathing abnormally.",
                "hamster",
                "choking",
                [
                    "Step 1: Move the hamster to a quiet area with fresh air.",
                    "Step 2: Avoid squeezing or excessive handling.",
                    "Step 3: Check for wheezing, clicking sounds, open-mouth breathing, or weakness.",
                    "Step 4: Keep dust, strong smells, and loose bedding away from the hamster.",
                    "Step 5: Contact an exotic-pet vet immediately if breathing does not improve.",
                ],
            ),
            make_guide(
                "Hamster Wound and Bleeding First Aid",
                "Emergency steps to control minor wounds and bleeding in hamsters.",
                "hamster",
                "bleeding",
                [
                    "Step 1: Place the hamster in a small secure container.",
                    "Step 2: Use clean gauze or tissue to apply very gentle pressure.",
                    "Step 3: Do not use strong antiseptics unless advised by a vet.",
                    "Step 4: Keep bedding clean, dry, and free of dust.",
                    "Step 5: Contact a vet if bleeding does not stop quickly.",
                ],
            ),
            make_guide(
                "Hamster Poisoning and Ingestion First Aid",
                "What to do if a hamster may have eaten unsafe food or a toxin.",
                "hamster",
                "poisoning",
                [
                    "Step 1: Remove unsafe food, chemicals, or bedding from the enclosure.",
                    "Step 2: Do not try to make the hamster vomit.",
                    "Step 3: Keep a sample or photo of the suspected toxin.",
                    "Step 4: Offer normal water access if the hamster is alert.",
                    "Step 5: Contact an exotic-pet vet urgently.",
                ],
            ),
            make_guide(
                "Hamster Fracture and Injury First Aid",
                "What to do if a hamster falls, limps, or may have a broken limb.",
                "hamster",
                "fracture",
                [
                    "Step 1: Move the hamster gently to a quiet, escape-proof container.",
                    "Step 2: Avoid squeezing, stretching, or examining the injured limb repeatedly.",
                    "Step 3: Remove wheels, climbing toys, and high platforms from the enclosure.",
                    "Step 4: Keep the hamster warm and reduce movement.",
                    "Step 5: Contact an exotic-pet vet if limping, swelling, or weakness is present.",
                ],
            ),
            make_guide(
                "Hamster Heatstroke and Shock First Aid",
                "Immediate steps for a hamster showing signs of overheating or collapse.",
                "hamster",
                "heatstroke",
                [
                    "Step 1: Move the cage away from sunlight or heat.",
                    "Step 2: Place the hamster in a cooler, quiet area.",
                    "Step 3: Offer water using a bottle or shallow dish.",
                    "Step 4: Do not place the hamster in cold water.",
                    "Step 5: Contact a vet if the hamster remains weak or unresponsive.",
                ],
            ),
            make_guide(
                "Guinea Pig Breathing Difficulty First Aid",
                "Emergency steps if a guinea pig is choking or breathing abnormally.",
                "guinea_pig",
                "choking",
                [
                    "Step 1: Keep the guinea pig calm and avoid stress.",
                    "Step 2: Move it to a quiet area with fresh air.",
                    "Step 3: Do not force food or water while breathing is laboured.",
                    "Step 4: Watch for wheezing, clicking sounds, or open-mouth breathing.",
                    "Step 5: Seek veterinary help immediately.",
                ],
            ),
            make_guide(
                "Guinea Pig Wound and Bleeding First Aid",
                "Emergency steps to control wounds and bleeding in guinea pigs.",
                "guinea_pig",
                "bleeding",
                [
                    "Step 1: Pick up the guinea pig gently and support the body.",
                    "Step 2: Apply a clean cloth or gauze to the wound.",
                    "Step 3: Use gentle pressure for several minutes.",
                    "Step 4: Keep the guinea pig in a clean, quiet space.",
                    "Step 5: Visit a vet if bleeding continues or the wound is deep.",
                ],
            ),
            make_guide(
                "Guinea Pig Poisoning and Ingestion First Aid",
                "What to do if a guinea pig may have eaten unsafe food or a toxin.",
                "guinea_pig",
                "poisoning",
                [
                    "Step 1: Remove the suspected unsafe food, plant, or chemical.",
                    "Step 2: Do not try to make the guinea pig vomit.",
                    "Step 3: Keep a sample or photo of what was eaten.",
                    "Step 4: Offer hay and water if the guinea pig is alert and breathing normally.",
                    "Step 5: Contact an exotic-pet vet urgently.",
                ],
            ),
            make_guide(
                "Guinea Pig Fracture and Injury First Aid",
                "How to protect a guinea pig with a suspected fracture or serious injury.",
                "guinea_pig",
                "fracture",
                [
                    "Step 1: Keep the guinea pig calm and prevent running or jumping.",
                    "Step 2: Support the whole body when lifting or moving it.",
                    "Step 3: Place it in a padded carrier with limited room to move.",
                    "Step 4: Do not try to splint or straighten an injured limb.",
                    "Step 5: Seek veterinary care urgently.",
                ],
            ),
            make_guide(
                "Guinea Pig Heatstroke and Shock First Aid",
                "Immediate steps for a guinea pig showing signs of heatstroke or shock.",
                "guinea_pig",
                "heatstroke",
                [
                    "Step 1: Move the guinea pig to a cool shaded area.",
                    "Step 2: Offer small amounts of cool water if alert.",
                    "Step 3: Gently dampen the ears and feet with cool water.",
                    "Step 4: Keep the guinea pig calm and away from strong direct airflow.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
        ]

        videos = [
            make_video(
                "Choking Cat - What to Do | First Aid for Pets",
                "Short first-aid guidance for helping a choking cat.",
                "cat",
                "choking",
                "https://www.youtube.com/watch?v=v_wsV8ADwvs",
                151,
            ),
            make_video(
                "Dog or Cat Bleeding? The First Thing I'd Do at Home",
                "Immediate home first-aid steps to control bleeding in cats and dogs.",
                "cat",
                "bleeding",
                "https://www.youtube.com/watch?v=Y9CZbzICCho",
                90,
            ),
            make_video(
                "React Appropriately to a Cat that has Been Poisoned",
                "Immediate response steps for suspected poisoning in cats.",
                "cat",
                "poisoning",
                "https://www.youtube.com/watch?v=-FukY7t_2AM",
                129,
            ),
            make_video(
                "Cat First Aid: How to Help a Cat with a Suspected Spinal Injury",
                "How to protect and move a cat with a suspected spinal injury.",
                "cat",
                "fracture",
                "https://www.youtube.com/watch?v=_mJYrbmbEl0",
                76,
            ),
            make_video(
                "Pet Emergency Tips: Heatstroke",
                "Best available short heatstroke first-aid video for overheated pets.",
                "cat",
                "heatstroke",
                "https://www.youtube.com/watch?v=uX_zdu9Z6m0",
                80,
            ),
            make_video(
                "Dog Choking Short Guide | First Aid for a Choking Dog",
                "Short guide for responding to a choking dog.",
                "dog",
                "choking",
                "https://www.youtube.com/watch?v=KMeNy4QD70I",
                72,
            ),
            make_video(
                "Dog Wound: How to Treat at Home",
                "Short guidance on first aid for a dog wound.",
                "dog",
                "bleeding",
                "https://www.youtube.com/watch?v=4yTPvSaQlls",
                66,
            ),
            make_video(
                "Dog Poisoning First Aid: What to Do If Your Pet is Poisoned",
                "Emergency response steps after suspected dog poisoning.",
                "dog",
                "poisoning",
                "https://www.youtube.com/watch?v=ke5rSgBQmvY",
                97,
            ),
            make_video(
                "How to Move an Injured Dog - First Aid for Pets",
                "How to safely move a dog with a suspected serious injury.",
                "dog",
                "fracture",
                "https://www.youtube.com/watch?v=N0SK_Iw-wcI",
                71,
            ),
            make_video(
                "Heatstroke First Aid For Dogs | Pet Health Advice",
                "Short first-aid advice for dog heatstroke.",
                "dog",
                "heatstroke",
                "https://www.youtube.com/watch?v=Uf1hsbSnhHo",
                74,
            ),
            make_video(
                "Choke in Rabbits",
                "Short rabbit-specific video on recognising choking.",
                "rabbit",
                "choking",
                "https://www.youtube.com/watch?v=W104HPrDF6U",
                175,
            ),
            make_video(
                "How to Stop Constant Bleeding if You Clip a Rabbit's Toenail Too Short",
                "Short rabbit-specific bleeding control guidance.",
                "rabbit",
                "bleeding",
                "https://www.youtube.com/watch?v=jwUyhY4l7zQ",
                37,
            ),
            make_video(
                "Poisoning in Rabbits | Wag!",
                "Short overview of poisoning risks and response for rabbits.",
                "rabbit",
                "poisoning",
                "https://www.youtube.com/watch?v=-rIP-YS79us",
                81,
            ),
            make_video(
                "Elderly and Disabled Rabbits - Poorly Healed Fractures",
                "Best available short rabbit fracture and injury fallback.",
                "rabbit",
                "fracture",
                "https://www.youtube.com/watch?v=1YCNPaqMgDA",
                140,
            ),
            make_video(
                "Heatstroke in Rabbits - What Every Bunny Parent Needs to Know",
                "Short rabbit-specific heatstroke guidance.",
                "rabbit",
                "heatstroke",
                "https://www.youtube.com/watch?v=teueqOV8-iw",
                144,
            ),
            make_video(
                "A Dwarf Hamster Has Respiratory Distress",
                "Short hamster-specific breathing distress video.",
                "hamster",
                "choking",
                "https://www.youtube.com/watch?v=JsIdu48k_9M",
                118,
            ),
            make_video(
                "Vet Case Study: Hamster with a Bleeding Eye",
                "Short hamster-specific bleeding vet case.",
                "hamster",
                "bleeding",
                "https://www.youtube.com/watch?v=CmsGrtkpKP4",
                109,
            ),
            make_video(
                "Safe and Unsafe Food for Hamsters",
                "Short guidance on foods that are unsafe for hamsters.",
                "hamster",
                "poisoning",
                "https://www.youtube.com/watch?v=mDunbvPDGVg",
                98,
            ),
            make_video(
                "Vet Case Study: Hamster with a Broken Leg",
                "Short hamster-specific broken leg vet case.",
                "hamster",
                "fracture",
                "https://www.youtube.com/watch?v=7l4re01nSbc",
                39,
            ),
            make_video(
                "How to Keep Your Hamster Cool in the Summer",
                "Short hamster-specific cooling guidance for heat risk.",
                "hamster",
                "heatstroke",
                "https://www.youtube.com/watch?v=ApxnzJ4SMAg",
                85,
            ),
            make_video(
                "Does Your Guinea Pig Have a Chronic Upper Respiratory Infection?",
                "Short guinea-pig breathing and respiratory warning video.",
                "guinea_pig",
                "choking",
                "https://www.youtube.com/watch?v=2mhe-edhOr0",
                137,
            ),
            make_video(
                "All Creatures Animal Clinic Tutorials: Guinea Pig Nail Trim",
                "Best available short guinea-pig nail and bleeding-care fallback.",
                "guinea_pig",
                "bleeding",
                "https://www.youtube.com/watch?v=JTPpMfjbbtY",
                157,
            ),
            make_video(
                "What Foods are Dangerous to a Guinea Pig?",
                "Short guidance on dangerous foods for guinea pigs.",
                "guinea_pig",
                "poisoning",
                "https://www.youtube.com/watch?v=lUA5d37wvVI",
                111,
            ),
            make_video(
                "Guinea Pig Compound Fracture Update - Broken Leg",
                "Short guinea-pig broken leg and fracture fallback.",
                "guinea_pig",
                "fracture",
                "https://www.youtube.com/watch?v=lsl50hFTbB8",
                103,
            ),
            make_video(
                "Signs of Heatstroke for Guinea Pigs",
                "Short heatstroke warning video for guinea pigs.",
                "guinea_pig",
                "heatstroke",
                "https://www.youtube.com/watch?v=TcXKvsX1maU",
                43,
            ),
        ]

        assign_authors(guides, author_ids)
        db.add_all(guides + videos)
        db.commit()

        print(f"Seeded {len(guides)} guides and {len(videos)} videos.")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

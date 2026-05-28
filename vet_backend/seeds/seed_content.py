"""
Seed script — populates the database with sample Guide and Video content.
Run from the project root:
    python -m app.scripts.seed_content
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal
from app.models.guide import Guide
from app.models.video import Video


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


def make_video(title, description, pet_type, emergency_category, video_url, duration_sec=180):
    return Video(
        title=title,
        description=description,
        petType=pet_type,
        emergencyCategory=emergency_category,
        publicationStatus="published",
        authorVetID=None,
        videoURL=video_url,
        durationSec=duration_sec,
    )


def seed():
    db = SessionLocal()

    try:
        guides = [
            # =========================
            # Cat First-Aid Guides
            # =========================
            make_guide(
                "How to Stop Bleeding in Cats",
                "Emergency steps to control bleeding in cats.",
                "cat",
                "bleeding",
                [
                    "Step 1: Stay calm and restrain the cat gently.",
                    "Step 2: Apply a clean cloth or gauze to the wound.",
                    "Step 3: Apply firm pressure for 5-10 minutes.",
                    "Step 4: Do not remove the cloth — add more on top if soaked.",
                    "Step 5: Rush to the vet immediately.",
                ],
            ),
            make_guide(
                "Cat Choking — First Response",
                "What to do if your cat is choking or struggling to breathe.",
                "cat",
                "choking",
                [
                    "Step 1: Check if the cat is coughing, gagging, or pawing at the mouth.",
                    "Step 2: Look inside the mouth only if it is safe to do so.",
                    "Step 3: Remove a visible object gently without pushing it deeper.",
                    "Step 4: Keep the cat calm and avoid giving food or water.",
                    "Step 5: Contact a vet immediately if breathing does not improve.",
                ],
            ),
            make_guide(
                "Cat Poisoning First Aid",
                "Immediate steps if a cat may have swallowed something toxic.",
                "cat",
                "poisoning",
                [
                    "Step 1: Move the cat away from the suspected poison.",
                    "Step 2: Do not make the cat vomit unless a vet instructs you.",
                    "Step 3: Keep the packaging or sample of the substance.",
                    "Step 4: Wipe the cat's mouth gently if poison is on the fur or lips.",
                    "Step 5: Call a vet or emergency clinic immediately.",
                ],
            ),
            make_guide(
                "Cat Burn First Aid",
                "Emergency steps for minor burns or scalds in cats.",
                "cat",
                "burn",
                [
                    "Step 1: Move the cat away from the heat source safely.",
                    "Step 2: Cool the burned area with clean cool water for several minutes.",
                    "Step 3: Do not apply creams, butter, or home remedies.",
                    "Step 4: Cover the area lightly with a clean cloth.",
                    "Step 5: Take the cat to a vet as soon as possible.",
                ],
            ),
            make_guide(
                "Cat Seizure Safety Steps",
                "How to keep a cat safe during and after a seizure.",
                "cat",
                "seizure",
                [
                    "Step 1: Move nearby objects away to prevent injury.",
                    "Step 2: Do not hold the cat down or place anything in its mouth.",
                    "Step 3: Keep the room quiet and dim if possible.",
                    "Step 4: Note how long the seizure lasts.",
                    "Step 5: Contact a vet immediately after the seizure ends.",
                ],
            ),

            # =========================
            # Dog First-Aid Guides
            # =========================
            make_guide(
                "Dog Choking — First Response",
                "What to do if your dog is choking on a foreign object.",
                "dog",
                "choking",
                [
                    "Step 1: Look into the dog's mouth for visible objects.",
                    "Step 2: If visible, carefully remove with fingers or tweezers.",
                    "Step 3: If not visible, perform back blows between shoulder blades.",
                    "Step 4: Perform abdominal thrusts if back blows fail.",
                    "Step 5: Go to the vet even if object is removed.",
                ],
            ),
            make_guide(
                "Dog Heatstroke First Aid",
                "Immediate steps for a dog showing signs of heatstroke.",
                "dog",
                "heatstroke",
                [
                    "Step 1: Move the dog to a cool, shaded area immediately.",
                    "Step 2: Offer small amounts of cool water if the dog is alert.",
                    "Step 3: Wet the dog's body with cool water, not ice water.",
                    "Step 4: Place the dog near a fan or moving air.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
            make_guide(
                "Dog Bleeding Control",
                "Emergency steps to control bleeding in dogs.",
                "dog",
                "bleeding",
                [
                    "Step 1: Keep the dog still and calm.",
                    "Step 2: Apply a clean cloth or gauze directly to the wound.",
                    "Step 3: Press firmly for 5-10 minutes without checking repeatedly.",
                    "Step 4: Add more cloth on top if blood soaks through.",
                    "Step 5: Bring the dog to a vet immediately.",
                ],
            ),
            make_guide(
                "Dog Poisoning First Aid",
                "What to do if your dog may have eaten something poisonous.",
                "dog",
                "poisoning",
                [
                    "Step 1: Remove the dog from the source of poison.",
                    "Step 2: Do not force vomiting unless told by a vet.",
                    "Step 3: Keep the product label, plant, or food sample if available.",
                    "Step 4: Observe symptoms such as drooling, shaking, or weakness.",
                    "Step 5: Call a vet or emergency clinic immediately.",
                ],
            ),
            make_guide(
                "Dog Paw Injury First Aid",
                "Simple first-aid steps for a cut or injured dog paw.",
                "dog",
                "paw-injury",
                [
                    "Step 1: Keep the dog calm and prevent running.",
                    "Step 2: Check the paw gently for cuts, thorns, or objects.",
                    "Step 3: Rinse the paw with clean water if dirty.",
                    "Step 4: Apply light pressure with a clean cloth if bleeding.",
                    "Step 5: Visit a vet if bleeding continues or the dog cannot walk.",
                ],
            ),

            # =========================
            # Rabbit First-Aid Guides
            # =========================
            make_guide(
                "Rabbit Heatstroke First Aid",
                "Immediate steps for a rabbit showing signs of heatstroke.",
                "rabbit",
                "heatstroke",
                [
                    "Step 1: Move rabbit to a cool, shaded area immediately.",
                    "Step 2: Dampen ears with cool (not cold) water.",
                    "Step 3: Place rabbit near a fan on low setting.",
                    "Step 4: Offer small amounts of cool water to drink.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
            make_guide(
                "Rabbit Not Eating — Urgent Response",
                "What to do if a rabbit suddenly stops eating.",
                "rabbit",
                "not-eating",
                [
                    "Step 1: Check if the rabbit is alert and moving normally.",
                    "Step 2: Offer fresh hay and water.",
                    "Step 3: Do not force food if the rabbit is weak or bloated.",
                    "Step 4: Keep the rabbit warm and quiet.",
                    "Step 5: Contact a vet urgently, as this can become serious quickly.",
                ],
            ),
            make_guide(
                "Rabbit Bleeding First Aid",
                "Emergency steps to control bleeding in rabbits.",
                "rabbit",
                "bleeding",
                [
                    "Step 1: Handle the rabbit gently and support the body.",
                    "Step 2: Apply a clean cloth or gauze to the bleeding area.",
                    "Step 3: Use gentle but firm pressure for several minutes.",
                    "Step 4: Keep the rabbit calm and reduce movement.",
                    "Step 5: Take the rabbit to a vet immediately.",
                ],
            ),
            make_guide(
                "Rabbit Broken Nail First Aid",
                "Simple steps for a rabbit with a broken or bleeding nail.",
                "rabbit",
                "broken-nail",
                [
                    "Step 1: Wrap the rabbit gently in a towel to reduce movement.",
                    "Step 2: Check which nail is injured.",
                    "Step 3: Apply gentle pressure with clean gauze.",
                    "Step 4: Keep the rabbit on a clean dry surface.",
                    "Step 5: Contact a vet if bleeding continues or the nail is badly torn.",
                ],
            ),
            make_guide(
                "Rabbit Breathing Difficulty",
                "Emergency steps if a rabbit is breathing abnormally.",
                "rabbit",
                "breathing",
                [
                    "Step 1: Keep the rabbit calm and avoid unnecessary handling.",
                    "Step 2: Move the rabbit to a quiet area with fresh air.",
                    "Step 3: Do not give food or water if breathing is laboured.",
                    "Step 4: Observe for open-mouth breathing or weakness.",
                    "Step 5: Seek emergency veterinary care immediately.",
                ],
            ),

            # =========================
            # Hamster First-Aid Guides
            # =========================
            make_guide(
                "Hamster Fall Injury First Aid",
                "What to do if a hamster falls or may be injured.",
                "hamster",
                "fall-injury",
                [
                    "Step 1: Move the hamster gently to a quiet, safe container.",
                    "Step 2: Avoid squeezing or excessive handling.",
                    "Step 3: Check for limping, bleeding, or difficulty moving.",
                    "Step 4: Keep the hamster warm and calm.",
                    "Step 5: Contact a vet if movement is abnormal or symptoms continue.",
                ],
            ),
            make_guide(
                "Hamster Bleeding First Aid",
                "Emergency steps to control minor bleeding in hamsters.",
                "hamster",
                "bleeding",
                [
                    "Step 1: Keep the hamster in a small secure container.",
                    "Step 2: Use clean gauze or tissue to apply gentle pressure.",
                    "Step 3: Do not use strong antiseptics unless advised by a vet.",
                    "Step 4: Keep bedding clean and dry.",
                    "Step 5: Contact a vet if bleeding does not stop quickly.",
                ],
            ),
            make_guide(
                "Hamster Heat Stress First Aid",
                "Immediate steps for a hamster showing signs of overheating.",
                "hamster",
                "heatstroke",
                [
                    "Step 1: Move the cage away from sunlight or heat.",
                    "Step 2: Place the hamster in a cooler quiet area.",
                    "Step 3: Offer water using a bottle or shallow dish.",
                    "Step 4: Do not place the hamster in cold water.",
                    "Step 5: Contact a vet if the hamster remains weak or unresponsive.",
                ],
            ),
            make_guide(
                "Hamster Wet Tail Warning",
                "Basic emergency response for signs of wet tail in hamsters.",
                "hamster",
                "wet-tail",
                [
                    "Step 1: Check for wetness around the tail area and diarrhoea.",
                    "Step 2: Separate the hamster from other pets if needed.",
                    "Step 3: Keep the cage clean, dry, and warm.",
                    "Step 4: Offer fresh water to prevent dehydration.",
                    "Step 5: Contact a vet urgently, as wet tail can become serious quickly.",
                ],
            ),
            make_guide(
                "Hamster Breathing Difficulty",
                "Emergency steps if a hamster is breathing abnormally.",
                "hamster",
                "breathing",
                [
                    "Step 1: Move the hamster to a quiet area with fresh air.",
                    "Step 2: Avoid handling the hamster more than necessary.",
                    "Step 3: Check for wheezing, clicking sounds, or open-mouth breathing.",
                    "Step 4: Keep the cage clean and away from dust or strong smells.",
                    "Step 5: Contact a vet immediately if breathing does not improve.",
                ],
            ),

            # =========================
            # Guinea Pig First-Aid Guides
            # =========================
            make_guide(
                "Guinea Pig Not Eating — Urgent Response",
                "What to do if a guinea pig suddenly stops eating.",
                "guinea pig",
                "not-eating",
                [
                    "Step 1: Check if the guinea pig is alert and moving.",
                    "Step 2: Offer fresh hay, vegetables, and clean water.",
                    "Step 3: Keep the guinea pig warm and quiet.",
                    "Step 4: Do not delay if eating does not resume.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
            make_guide(
                "Guinea Pig Heatstroke First Aid",
                "Immediate steps for a guinea pig showing signs of heatstroke.",
                "guinea pig",
                "heatstroke",
                [
                    "Step 1: Move the guinea pig to a cool shaded area.",
                    "Step 2: Offer small amounts of cool water.",
                    "Step 3: Gently dampen the ears and feet with cool water.",
                    "Step 4: Keep the guinea pig calm and away from direct airflow that is too strong.",
                    "Step 5: Contact a vet urgently.",
                ],
            ),
            make_guide(
                "Guinea Pig Bleeding First Aid",
                "Emergency steps to control bleeding in guinea pigs.",
                "guinea pig",
                "bleeding",
                [
                    "Step 1: Pick up the guinea pig gently and support the body.",
                    "Step 2: Apply a clean cloth or gauze to the wound.",
                    "Step 3: Use gentle pressure for several minutes.",
                    "Step 4: Keep the guinea pig in a clean and quiet space.",
                    "Step 5: Visit a vet if bleeding continues or the wound is deep.",
                ],
            ),
            make_guide(
                "Guinea Pig Breathing Difficulty",
                "Emergency steps if a guinea pig is breathing abnormally.",
                "guinea pig",
                "breathing",
                [
                    "Step 1: Keep the guinea pig calm and avoid stress.",
                    "Step 2: Move it to a quiet area with fresh air.",
                    "Step 3: Do not force food or water.",
                    "Step 4: Watch for wheezing, clicking sounds, or open-mouth breathing.",
                    "Step 5: Seek veterinary help immediately.",
                ],
            ),
            make_guide(
                "Guinea Pig Broken Nail First Aid",
                "Simple steps for a guinea pig with a broken or bleeding nail.",
                "guinea pig",
                "broken-nail",
                [
                    "Step 1: Hold the guinea pig gently and support its body.",
                    "Step 2: Check the injured nail without pulling it.",
                    "Step 3: Apply gentle pressure with clean gauze or tissue.",
                    "Step 4: Keep the guinea pig on clean dry bedding.",
                    "Step 5: Contact a vet if bleeding continues or the nail is badly damaged.",
                ],
            ),
        ]

        videos = [
            # =========================
            # Cat First-Aid Videos
            # =========================
            make_video(
                "Video: How to Stop Bleeding in Cats",
                "Video guide showing how to control bleeding in cats.",
                "cat",
                "bleeding",
                "https://example.com/videos/cat-bleeding.mp4",
                210,
            ),
            make_video(
                "Video: Cat Choking First Response",
                "Video guide showing what to do when a cat is choking.",
                "cat",
                "choking",
                "https://example.com/videos/cat-choking.mp4",
                200,
            ),
            make_video(
                "Video: Cat Poisoning First Aid",
                "Video guide explaining immediate response for suspected poisoning in cats.",
                "cat",
                "poisoning",
                "https://example.com/videos/cat-poisoning.mp4",
                220,
            ),
            make_video(
                "Video: Cat Burn First Aid",
                "Video guide showing safe first-aid steps for cat burns or scalds.",
                "cat",
                "burn",
                "https://example.com/videos/cat-burn.mp4",
                190,
            ),
            make_video(
                "Video: Cat Seizure Safety Steps",
                "Video guide showing how to keep a cat safe during and after a seizure.",
                "cat",
                "seizure",
                "https://example.com/videos/cat-seizure.mp4",
                230,
            ),

            # =========================
            # Dog First-Aid Videos
            # =========================
            make_video(
                "Video: Dog Choking First Response",
                "Video guide showing first response steps for choking in dogs.",
                "dog",
                "choking",
                "https://example.com/videos/dog-choking.mp4",
                200,
            ),
            make_video(
                "Video: Dog Heatstroke First Aid",
                "Video guide showing how to cool a dog safely during heatstroke.",
                "dog",
                "heatstroke",
                "https://example.com/videos/dog-heatstroke.mp4",
                210,
            ),
            make_video(
                "Video: Dog Bleeding Control",
                "Video guide showing how to control bleeding in dogs.",
                "dog",
                "bleeding",
                "https://example.com/videos/dog-bleeding.mp4",
                220,
            ),
            make_video(
                "Video: Dog Poisoning First Aid",
                "Video guide explaining what to do if a dog may have eaten poison.",
                "dog",
                "poisoning",
                "https://example.com/videos/dog-poisoning.mp4",
                230,
            ),
            make_video(
                "Video: Dog Paw Injury First Aid",
                "Video guide showing simple first-aid steps for injured dog paws.",
                "dog",
                "paw-injury",
                "https://example.com/videos/dog-paw-injury.mp4",
                180,
            ),

            # =========================
            # Rabbit First-Aid Videos
            # =========================
            make_video(
                "Video: Rabbit Heatstroke First Aid",
                "Video guide showing how to respond to rabbit heatstroke.",
                "rabbit",
                "heatstroke",
                "https://example.com/videos/rabbit-heatstroke.mp4",
                210,
            ),
            make_video(
                "Video: Rabbit Not Eating Urgent Response",
                "Video guide explaining what to do when a rabbit stops eating.",
                "rabbit",
                "not-eating",
                "https://example.com/videos/rabbit-not-eating.mp4",
                220,
            ),
            make_video(
                "Video: Rabbit Bleeding First Aid",
                "Video guide showing how to control bleeding in rabbits.",
                "rabbit",
                "bleeding",
                "https://example.com/videos/rabbit-bleeding.mp4",
                200,
            ),
            make_video(
                "Video: Rabbit Broken Nail First Aid",
                "Video guide showing how to handle a rabbit broken nail emergency.",
                "rabbit",
                "broken-nail",
                "https://example.com/videos/rabbit-broken-nail.mp4",
                180,
            ),
            make_video(
                "Video: Rabbit Breathing Difficulty",
                "Video guide explaining emergency response for rabbit breathing difficulty.",
                "rabbit",
                "breathing",
                "https://example.com/videos/rabbit-breathing.mp4",
                230,
            ),

            # =========================
            # Hamster First-Aid Videos
            # =========================
            make_video(
                "Video: Hamster Fall Injury First Aid",
                "Video guide showing what to do if a hamster falls or is injured.",
                "hamster",
                "fall-injury",
                "https://example.com/videos/hamster-fall-injury.mp4",
                170,
            ),
            make_video(
                "Video: Hamster Bleeding First Aid",
                "Video guide showing how to control minor bleeding in hamsters.",
                "hamster",
                "bleeding",
                "https://example.com/videos/hamster-bleeding.mp4",
                180,
            ),
            make_video(
                "Video: Hamster Heat Stress First Aid",
                "Video guide explaining immediate response for hamster overheating.",
                "hamster",
                "heatstroke",
                "https://example.com/videos/hamster-heatstroke.mp4",
                190,
            ),
            make_video(
                "Video: Hamster Wet Tail Warning",
                "Video guide explaining warning signs and urgent response for wet tail.",
                "hamster",
                "wet-tail",
                "https://example.com/videos/hamster-wet-tail.mp4",
                210,
            ),
            make_video(
                "Video: Hamster Breathing Difficulty",
                "Video guide explaining emergency response for hamster breathing difficulty.",
                "hamster",
                "breathing",
                "https://example.com/videos/hamster-breathing.mp4",
                200,
            ),

            # =========================
            # Guinea Pig First-Aid Videos
            # =========================
            make_video(
                "Video: Guinea Pig Not Eating Urgent Response",
                "Video guide explaining what to do when a guinea pig stops eating.",
                "guinea pig",
                "not-eating",
                "https://example.com/videos/guinea-pig-not-eating.mp4",
                220,
            ),
            make_video(
                "Video: Guinea Pig Heatstroke First Aid",
                "Video guide showing how to respond to guinea pig heatstroke.",
                "guinea pig",
                "heatstroke",
                "https://example.com/videos/guinea-pig-heatstroke.mp4",
                210,
            ),
            make_video(
                "Video: Guinea Pig Bleeding First Aid",
                "Video guide showing how to control bleeding in guinea pigs.",
                "guinea pig",
                "bleeding",
                "https://example.com/videos/guinea-pig-bleeding.mp4",
                200,
            ),
            make_video(
                "Video: Guinea Pig Breathing Difficulty",
                "Video guide explaining emergency response for guinea pig breathing difficulty.",
                "guinea pig",
                "breathing",
                "https://example.com/videos/guinea-pig-breathing.mp4",
                230,
            ),
            make_video(
                "Video: Guinea Pig Broken Nail First Aid",
                "Video guide showing simple first-aid steps for a broken guinea pig nail.",
                "guinea pig",
                "broken-nail",
                "https://example.com/videos/guinea-pig-broken-nail.mp4",
                180,
            ),
        ]

        db.add_all(guides + videos)
        db.commit()

        print(f"✅ Seeded {len(guides)} guides and {len(videos)} videos.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
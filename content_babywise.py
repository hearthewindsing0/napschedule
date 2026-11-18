# Babywise (eat-wake-sleep) stages.
# Source for naps/day and total sleep by week, feeding minimums and sample-day shapes:
# "On Becoming Babywise" (25th Anniversary Edition), Gary Ezzo & Robert Bucknam, MD,
# and the publisher's companion chart PDF. Everything is summarized in our own words.
# Waketime lengths are OUR estimates (the book gives few exact figures); they are labeled as such.
#
# cycles: (minutes after first feed, feed label, waketime incl. feeding in minutes, nap label)
#   nap label "night" = down for the night; None = no nap after this feed.
# night: extra rows (minutes after first feed, label)

BOOK = "On Becoming Babywise (25th Anniversary Edition) by Gary Ezzo and Robert Bucknam, MD"

BW_STAGES = [
    {
        "key": "bw-1-2w", "slug": "babywise-schedule-weeks-1-2", "label": "Weeks 1–2",
        "title": "Babywise Schedule Weeks 1–2: Newborn Eat-Wake-Sleep Routine",
        "desc": "What a Babywise-style day looks like in the first two weeks: feeds about every 2.5 hours, 5–6 naps, and the signs your newborn is eating enough.",
        "naps": "5–6", "sleep": "17–19 hours", "feeds": "8–10 (at least 8)", "interval": "About every 2.5 hours, counted from the start of one feed to the start of the next",
        "waketime": "Very little beyond the feed itself",
        "cycles": [(0, "Feed", 50, "Nap"), (150, "Feed", 50, "Nap"), (300, "Feed", 50, "Nap"), (450, "Feed", 50, "Nap"),
                   (600, "Feed", 50, "Nap"), (750, "Feed", 50, "Nap"), (900, "Late-evening feed", 40, "night")],
        "night": [(1110, "Night feed"), (1260, "Night feed")],
        "intro": """<p>In the first two weeks, the Babywise approach is mostly about <strong>full feedings</strong> and a gentle order to the day: feed, a few minutes awake for burping and a diaper change, then sleep. The book calls this the feed-wake-sleep cycle. At this age, "waketime" is short, because a newborn spends most of their awake time eating.</p>
<p>Babywise suggests feeding roughly every 2.5 hours during the day, and not letting more than about 3 hours pass between daytime feeds in the first weeks. Expect 8 to 10 feeds in 24 hours, including night feeds.</p>""",
        "tips": [
            "Aim for full feeds rather than snacking. Keep a sleepy newborn gently awake while eating (undress them a little, tickle their feet).",
            "Feed your baby if they show hunger cues before the clock says it's time. Babywise itself says the clock is a guide, not the boss.",
            "Watch the diapers. In week 1, look for at least 8 feeds a day and an increasing number of wet diapers; by the end of week 1, about 6 or more wet diapers a day is typical.",
            "Don't try to stretch nights yet. Night feeds are expected at this age.",
        ],
    },
    {
        "key": "bw-3-5w", "slug": "babywise-schedule-weeks-3-5", "label": "Weeks 3–5",
        "title": "Babywise Schedule Weeks 3–5: Sample Day and Waketimes",
        "desc": "A Babywise-style schedule for weeks 3 to 5: feeds every 2.5–3 hours, short waketimes, 1.5–2 hour naps and a sample day.",
        "naps": "5–6", "sleep": "16–18 hours", "feeds": "At least 8 (7–8 by week 5)", "interval": "Every 2.5–3 hours during the day",
        "waketime": "About 20 minutes or a bit more after the feed",
        "cycles": [(0, "Feed", 60, "Nap"), (165, "Feed", 60, "Nap"), (330, "Feed", 60, "Nap"), (495, "Feed", 60, "Nap"),
                   (660, "Feed", 60, "Nap"), (810, "Feed", 60, "Nap"), (960, "Late-evening feed", 40, "night")],
        "night": [(1200, "Night feed")],
        "intro": """<p>Between weeks 3 and 5, babies start to have a little real waketime after eating. In the Babywise model, feeding, burping and changing take about half an hour, followed by a short stretch awake, then a nap of roughly 1.5 to 2 hours before the next feed.</p>
<p>Daytime feeds usually land 2.5 to 3 hours apart. The book's goal is a predictable rhythm, with the first feed of the morning at the same time each day.</p>""",
        "tips": [
            "Pick a consistent first-feed time (for example, 7:00 AM) and wake your baby for it. That anchors the whole day.",
            "Keep waketime calm: a few minutes on a play mat, looking at faces, a short walk.",
            "If a nap ends early and your baby is genuinely hungry, feed them. Then return to the routine at the next cycle.",
            "Keep checking diapers and weight gain with your pediatrician.",
        ],
    },
    {
        "key": "bw-6-7w", "slug": "babywise-schedule-weeks-6-7", "label": "Weeks 6–7",
        "title": "Babywise Schedule Weeks 6–7: Longer Night Stretches",
        "desc": "Babywise-style day for weeks 6–7: about 3 hours between feeds, 4–6 naps, and how the night starts to stretch.",
        "naps": "4–6", "sleep": "15–18 hours", "feeds": "7–8", "interval": "About every 2.5–3 hours",
        "waketime": "Around an hour including the feed",
        "cycles": [(0, "Feed", 70, "Nap"), (180, "Feed", 70, "Nap"), (360, "Feed", 70, "Nap"), (540, "Feed", 70, "Nap"),
                   (690, "Feed", 60, "Evening sleep until the late feed"), (930, "Late-evening feed", 40, "night")],
        "night": [(1230, "Night feed (if still needed)")],
        "intro": """<p>Around weeks 6 and 7, many babies on an eat-wake-sleep routine begin stretching their longest sleep at night. Babywise describes this as the first of several "merges," where two feeds gradually become one as your baby takes more at each feeding.</p>
<p>Daytime feeds settle at roughly 3 hours apart, with a late-evening feed before the longest night stretch.</p>""",
        "tips": [
            "Let your baby, not the calendar, decide when a night feed drops. If they wake hungry, feed them.",
            "Keep night feeds quiet and dark so they stay all business.",
            "Total feeds should still be around 7–8 in 24 hours. If they drop well below that, talk with your pediatrician.",
        ],
    },
    {
        "key": "bw-8-12w", "slug": "babywise-schedule-weeks-8-12", "label": "Weeks 8–12",
        "title": "Babywise Schedule 8–12 Weeks (2–3 Months): Sample Day",
        "desc": "A Babywise-style 2 to 3 month schedule: 3-hour feed-wake-sleep cycles, 4–5 naps, a late-evening feed and longer nights.",
        "naps": "4–5", "sleep": "14–17 hours", "feeds": "6–8 (the book lists at least 7 through week 10)", "interval": "About every 3 hours",
        "waketime": "About 60–90 minutes including the feed",
        "cycles": [(0, "Feed", 80, "Nap"), (150, "Feed", 90, "Nap"), (330, "Feed", 90, "Nap"), (510, "Feed", 90, "Nap"),
                   (660, "Feed", 90, "Evening sleep until the late feed"), (945, "Late-evening feed", 40, "night")],
        "night": [(1260, "Night feed if your baby wakes hungry")],
        "intro": """<p>This is the stage most parents picture when they think of Babywise. The day falls into about five 3-hour cycles, plus a late-evening feed around 10:30 to 11 PM. Babywise says many babies who follow the routine sleep through the night somewhere around 8 to 12 weeks. Plenty of healthy babies take longer, and that's normal too.</p>
<p>Waketime is now long enough for real play: tummy time, songs, a walk outside.</p>""",
        "tips": [
            "If your baby still wakes at night hungry, feed them. A long night stretch comes from full daytime feeds, not from ignoring hunger.",
            "Protect the late-evening feed for now; it's the one that usually carries babies through the night.",
            "Bring your baby to their pediatrician visits and keep an eye on weight gain as nights lengthen.",
        ],
    },
    {
        "key": "bw-13-15w", "slug": "babywise-schedule-weeks-13-15", "label": "Weeks 13–15",
        "title": "Babywise Schedule 13–15 Weeks (3 Months): Sample Day",
        "desc": "Babywise-style 3 month schedule: 3-hour cycles, 3–4 naps including a catnap, a 7 PM bedtime feed and an optional late feed.",
        "naps": "3–4", "sleep": "13–17 hours", "feeds": "About 5–6", "interval": "About every 3 hours",
        "waketime": "About 1.5 hours including the feed",
        "cycles": [(0, "Feed", 90, "Nap"), (180, "Feed", 90, "Nap"), (360, "Feed", 90, "Nap"), (540, "Feed", 90, "Catnap"),
                   (720, "Bedtime feed", 30, "night")],
        "night": [(900, "Late-evening feed (often dropped between 13 and 24 weeks)")],
        "intro": """<p>At around three months, the Babywise day has a clear shape: about four daytime cycles and a bedtime feed in the early evening. Many families still offer a late-evening feed, which the book describes as one of the next feeds to merge away as daytime feeds get fuller.</p>
<p>The last nap of the day is often a short catnap that bridges the gap to bedtime.</p>""",
        "tips": [
            "Drop the late-evening feed gradually (move it a little earlier or shorten it) rather than all at once.",
            "If naps shorten during the 4-month sleep changes, keep the cycle order the same and give it a week or two.",
        ],
    },
    {
        "key": "bw-16-24w", "slug": "babywise-schedule-weeks-16-24", "label": "Weeks 16–24 (4–5 months)",
        "title": "Babywise 4–5 Month Schedule (16–24 Weeks): Sample Day",
        "desc": "Babywise-style 4 and 5 month schedule: five feed-wake-sleep cycles, 3–4 naps with a catnap, and an 8 PM bedtime.",
        "naps": "3–4", "sleep": "13–16 hours", "feeds": "About 5", "interval": "About every 3–3.5 hours",
        "waketime": "About 1.5–2 hours including the feed",
        "cycles": [(0, "Feed", 105, "Nap"), (195, "Feed", 105, "Nap"), (390, "Feed", 105, "Nap"), (585, "Feed", 60, "Catnap (30–45 min)"),
                   (780, "Bedtime feed", 30, "night")],
        "night": [],
        "intro": """<p>By four to five months, Babywise describes a day of about five cycles: four daytime feeds and a liquid feed before bed around 8 PM. The late-evening feed is usually gone by this point.</p>
<p>Ask your pediatrician about starting solids; the AAP recommends introducing solid foods around 6 months, when your baby shows signs of readiness.</p>""",
        "tips": [
            "Keep the catnap short so bedtime stays on track.",
            "If your baby starts waking at night again, check whether daytime feeds have gotten shorter or more distracted.",
        ],
    },
    {
        "key": "bw-25-38w", "slug": "babywise-schedule-6-9-months", "label": "Weeks 25–38 (6–9 months)",
        "title": "Babywise 6–9 Month Schedule (25–38 Weeks): Sample Day",
        "desc": "Babywise-style schedule for 6 to 9 months: five cycles with solids, 2–3 naps, dropping the catnap, and an 8 PM bedtime.",
        "naps": "2–3", "sleep": "13–15 hours", "feeds": "About 4–5 milk feeds plus solids", "interval": "About every 3.5 hours",
        "waketime": "About 2–2.5 hours",
        "cycles": [(0, "Milk + breakfast", 120, "Nap"), (210, "Milk", 135, "Nap"), (420, "Milk + solids", 150, "Catnap (30–45 min)"),
                   (630, "Dinner (solids)", None, None), (780, "Bedtime milk feed", 30, "night")],
        "night": [],
        "intro": """<p>From about six months, solid foods join the routine and the Babywise day slowly shifts toward family mealtimes. The book's samples for this stage show five cycles with a mid-afternoon catnap, and later four cycles once the catnap and one milk feed merge away (often somewhere between 28 and 40 weeks).</p>
<p>Most babies take two solid naps plus a short catnap here, before dropping to two naps.</p>""",
        "tips": [
            "Offer milk first, then solids, at the early meals, unless your pediatrician advises otherwise.",
            "When the catnap starts pushing bedtime late or gets refused, it's time to drop it.",
        ],
    },
    {
        "key": "bw-39-52w", "slug": "babywise-schedule-9-12-months", "label": "Weeks 39–52 (9–12 months)",
        "title": "Babywise 9–12 Month Schedule (39–52 Weeks): Sample Day",
        "desc": "Babywise-style schedule for 9 to 12 months: three meals plus snacks, 2 naps, and an 8 PM bedtime.",
        "naps": "2", "sleep": "12–15 hours", "feeds": "3 meals, 1–2 snacks, milk", "interval": "Meals about 4–5 hours apart",
        "waketime": "About 2.5–3 hours",
        "cycles": [(0, "Breakfast + milk", 150, "Nap"), (270, "Lunch + milk", 165, "Nap"), (570, "Snack", None, None),
                   (690, "Family dinner", None, None), (750, "Bath, books and bedtime routine", 30, "night")],
        "night": [],
        "intro": """<p>Toward the first birthday, the Babywise routine looks a lot like a family schedule: breakfast, a morning nap, lunch, an afternoon nap, a snack, family dinner and an 8 PM bedtime. The book notes that by around 46 to 52 weeks, many babies no longer need a liquid feed before bed.</p>
<p>From here, the Ezzos' follow-up books (<em>Babywise II</em>, <em>On Becoming Pretoddlerwise</em> and <em>On Becoming Toddlerwise</em>) cover the move to one nap and toddler routines.</p>""",
        "tips": [
            "Keep naps in the crib at consistent times; two naps usually last until somewhere between 13 and 18 months.",
            "Talk with your pediatrician about milk amounts and switching to whole milk around 12 months.",
        ],
    },
]

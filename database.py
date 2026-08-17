AIRCRAFT_DB = {
    "332": {
        "name": "Airbus A330-200",
        "desc": (
            "Wide-body twinjet. Uncommon visitor at Cairns (YBCS), classified"
            " as a rare heavy."
        ),
        "rare": True,
    },
    "333": {
        "name": "Airbus A330-300",
        "desc": (
            "Stretched wide-body twinjet. Rare widebody visitor at Cairns."
        ),
        "rare": True,
    },
    "763": {
        "name": "Boeing 767-300",
        "desc": "Wide-body twinjet used for specialized or freight runs.",
        "rare": True,
    },
    "388": {
        "name": "Airbus A380-800",
        "desc": "Double-deck widebody giant. Extremely rare at YBCS.",
        "rare": True,
    },
    "788": {
        "name": "Boeing 787-8 Dreamliner",
        "desc": (
            "Wide-body, long-range twin-engine jet (Regular international"
            " visitor)."
        ),
        "rare": False,
    },
    "789": {
        "name": "Boeing 787-9 Dreamliner",
        "desc": "Stretched Dreamliner (Regular international visitor).",
        "rare": False,
    },
    "350": {
        "name": "Airbus A350-900",
        "desc": "Carbon-composite widebody long-haul airliner.",
        "rare": False,
    },
    "359": {
        "name": "Airbus A350-900",
        "desc": "Advanced widebody twinjet.",
        "rare": False,
    },
    "C130": {
        "name": "Lockheed C-130 Hercules / NZ7011",
        "desc": (
            "Military tactical transport aircraft. Automatically flagged as"
            " military."
        ),
        "rare": True,
        "military": True,
    },
    "ATF": {
        "name": "Alenia C-27J Spartan",
        "desc": "Tactical military transport aircraft.",
        "rare": True,
        "military": True,
    },
    "737": {
        "name": "Boeing 737-800 / 73G",
        "desc": "Narrow-body twinjet airliner, domestic workhorse.",
        "rare": False,
    },
    "738": {
        "name": "Boeing 737-800",
        "desc": "Standard single-aisle twinjet.",
        "rare": False,
    },
    "73H": {
        "name": "Boeing 737-800 (Winglets)",
        "desc": "Equipped with blended winglets.",
        "rare": False,
    },
    "7M8": {
        "name": "Boeing 737 MAX 8",
        "desc": "Next-generation CFM LEAP-1B powered narrow-body airliner.",
        "rare": False,
    },
    "7M9": {
        "name": "Boeing 737 MAX 9",
        "desc": "High-capacity stretched variant of the MAX family.",
        "rare": False,
    },
    "14Y": {
        "name": "Boeing 737-800BCF (Cargo)",
        "desc": "Boeing Converted Freighter variant.",
        "rare": False,
    },
    "14Z": {
        "name": "Boeing 737-300SF (Cargo)",
        "desc": "Special Freighter variant configured for palletized freight.",
        "rare": False,
    },
    "320": {
        "name": "Airbus A320-200",
        "desc": "Popular short-to-medium-range single-aisle passenger jet.",
        "rare": False,
    },
    "321": {
        "name": "Airbus A321-200",
        "desc": "Stretched fuselage version of the A320 family.",
        "rare": False,
    },
    "32Q": {
        "name": "Airbus A321neo",
        "desc": "New Engine Option variant featuring sharklets.",
        "rare": False,
    },
    "223": {
        "name": "Airbus A220-300",
        "desc": "Advanced ultra-efficient small single-aisle regional jet.",
        "rare": False,
    },
    "DH1": {
        "name": "De Havilland DHC-6 Twin Otter",
        "desc": "Rugged STOL utility transport aircraft.",
        "rare": False,
    },
    "DH2": {
        "name": "De Havilland Dash 8-200",
        "desc": "Twin-turboprop regional airliner.",
        "rare": False,
    },
    "DH4": {
        "name": "De Havilland Dash 8-Q400",
        "desc": "High-speed modern turboprop regional airliner.",
        "rare": False,
    },
    "E90": {
        "name": "Embraer E190",
        "desc": "Medium-range regional jet.",
        "rare": False,
    },
    "SF3": {
        "name": "Saab 340",
        "desc": "Swedish twin-turboprop commuter aircraft.",
        "rare": False,
    },
    "AT7": {
        "name": "ATR 72-600",
        "desc": "Modern regional turboprop optimized for fuel economy.",
        "rare": False,
    },
    "BE20": {
        "name": "Beechcraft King Air 200",
        "desc": "Pressurized twin-turboprop workhorse.",
        "rare": False,
    },
}

AIRLINE_DB = {
    "QF": {
        "name": "Qantas Airways",
        "desc": "Australia's flag carrier and largest airline.",
        "military": False,
    },
    "JQ": {
        "name": "Jetstar Airways",
        "desc": "Australian low-cost airline subsidiary of Qantas.",
        "military": False,
    },
    "VA": {
        "name": "Virgin Australia",
        "desc": "Major Australian domestic and international airline.",
        "military": False,
    },
    "QN": {
        "name": "Skytrans Airlines",
        "desc": "Regional airline operating out of Cairns.",
        "military": False,
    },
    "ZL": {
        "name": "Regional Express (Rex)",
        "desc": "Australian regional and domestic airline.",
        "military": False,
    },
    "QQ": {
        "name": "Alliance Airlines",
        "desc": "Australian contract and charter specialist airline.",
        "military": False,
    },
    "PX": {
        "name": "Air Niugini",
        "desc": "National airline of Papua New Guinea.",
        "military": False,
    },
    "NZ": {
        "name": "Air New Zealand",
        "desc": "Flag carrier airline of New Zealand.",
        "military": False,
    },
    "FJ": {
        "name": "Fiji Airways",
        "desc": "International flag carrier of Fiji.",
        "military": False,
    },
    "SQ": {
        "name": "Singapore Airlines",
        "desc": "Flag carrier of Singapore.",
        "military": False,
    },
    "TL": {
        "name": "Airnorth",
        "desc": "Northern Australia regional airline based in Darwin.",
        "military": False,
    },
    "MAC": {
        "name": "Mission Aviation Fellowship / Charter",
        "desc": "Specialized regional mission and remote charter operator.",
        "military": False,
    },
    "PVT": {
        "name": "Private / General Aviation",
        "desc": "Private or corporate general aviation movement.",
        "military": False,
    },
    "KIW": {
        "name": "Royal New Zealand Air Force (RNZAF)",
        "desc": "Military transport and logistics flight.",
        "military": True,
    },
    "ASY": {
        "name": "Australian Defence Force (ADF - 'ASY')",
        "desc": "Official callsign prefix for Royal Australian Air Force flights.",
        "military": True,
    },
    "VM": {
        "name": "United States Marine Corps (USMC Aviation)",
        "desc": "US Marine aviation detachment or tactical transport squadron.",
        "military": True,
    },
    "USMC": {
        "name": "United States Marine Corps",
        "desc": "United States Marine Corps military air transport.",
        "military": True,
    },
    "RCH": {
        "name": "US Air Force Air Mobility Command ('Reach')",
        "desc": "United States military global strategic airlift command.",
        "military": True,
    },
    "CNV": {
        "name": "United States Navy ('Convoy')",
        "desc": "US Navy tactical and logistical transport flight.",
        "military": True,
    },
}
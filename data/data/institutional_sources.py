from core.audit import Source

UNIVERSITIES = [
    Source("Oxford University", "https://www.ox.ac.uk/", "university"),
    Source("University of Cambridge", "https://www.cam.ac.uk/", "university"),
    Source("Harvard University", "https://www.harvard.edu/", "university"),
    Source("MIT", "https://www.mit.edu/", "university"),
    Source("Yale University", "https://www.yale.edu/", "university"),
    Source("New York University (NYU)", "https://www.nyu.edu/", "university"),
    Source("Sorbonne University", "https://www.sorbonne-universite.fr/en", "university"),
    Source("University of Bologna", "https://www.unibo.it/en", "university"),
    Source("Sapienza University of Rome", "https://www.uniroma1.it/en", "university"),
    Source("Politecnico di Milano", "https://www.polimi.it/en", "university"),
    Source("IUAV University of Venice", "https://www.iuav.it/en/", "university"),
    Source("Berklee College of Music", "https://www.berklee.edu/", "university"),
]

MUSEUMS = [
    Source("Uffizi Galleries", "https://www.uffizi.it/en", "museum"),
    Source("Vatican Museums", "https://www.museivaticani.va/", "museum"),
    Source("The National Gallery (UK) · Research", "https://www.nationalgallery.org.uk/research", "museum"),
    Source("MAXXI · National Museum of 21st Century Arts", "https://www.maxxi.art/en/", "museum"),
]

REFERENCE_WORKS = [
    Source("Stanford Encyclopedia of Philosophy (SEP)", "https://plato.stanford.edu/", "university"),
    Source("Oxford Music Online", "https://www.oxfordmusiconline.com/", "university"),
    Source("Cambridge University Press · Music", "https://www.cambridge.org/core/what-we-publish/subjects/music", "university"),
]

PLATFORMS = [
    Source("Epic Games Store · Free Games", "https://store.epicgames.com/en-US/free-games", "official_platform"),
    Source("Epic Games Store · Free Games JSON endpoint", "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions", "official_platform_api"),
    Source("Amazon · Prime Gaming", "https://www.amazon.com/prime-gaming", "official_platform"),
    Source("GOG · Free Games", "https://www.gog.com/en/partner/free_games", "official_platform"),
    Source("GOG.com · Filtered catalog endpoint (price=free)", "https://www.gog.com/games/ajax/filtered?mediaType=game&price=free&page=1", "official_platform_api"),
    Source("Twitch · Drops Inventory", "https://www.twitch.tv/drops/inventory", "official_platform"),
    Source("Twitch · Drops Enabled Directory", "https://www.twitch.tv/directory/collection/drops-enabled", "official_platform"),
]

AWARDS = [
    Source("BAFTA · Games Awards", "https://www.bafta.org/awards/games/", "official_archive"),
    Source("BAFTA · Awards Search", "https://www.bafta.org/awards/search/", "official_archive"),
    Source("The Game Awards · Winners", "https://thegameawards.com/winners", "official_archive"),
    Source("The Game Awards · Rewind", "https://thegameawards.com/rewind", "official_archive"),
    Source("AIAS · Awards (D.I.C.E.)", "https://www.interactive.org/awards/", "official_archive"),
]

PUBLICATIONS = [
    Source("PC Gamer", "https://www.pcgamer.com/", "official_platform"),
    Source("Game Developer", "https://www.gamedeveloper.com/", "official_platform"),
    Source("BAFTA", "https://www.bafta.org/", "official_archive"),
]

import requests
from ayumi import Ayumi
from time import sleep

_JIKAN_USER_WATCHING = "https://api.jikan.moe/v3/user/{}/animelist/watching/{}"
_JIKAN_USER_PTW = "https://api.jikan.moe/v3/user/{}/animelist/plantowatch/{}"

def _fetch_list(user, listurl, listname):
    """
    Helper method to get a user's anime list.
    Doesn't handle errors, just raises them. Needs to be called by a wrapper.

    Params:
        User: Username of MAL user
        listurl: URL to use to fetch info
        listname: Watching, Plan to Watch (for logging)
    """

    anime = list()

    try:
        jikan_res = requests.get(listurl.format(user, ""))
        
        # Verify status code
        if jikan_res.status_code != 200:
            Ayumi.debug("jikan mode returned a bad status code on attempt to get {}'s {} list.".format(user, listname))
            raise Exception()
    
        # Make sure an anime actually exists undeer this name
        try:
            jikan_res_json = jikan_res.json()
        except:
            jikan_res_json = dict() # Clean handling
        
        if 'anime' not in jikan_res_json:
            Ayumi.debug("Jikan.moe did not return an anime list on attempt to get {}'s {} list.".format(user, listname))
            raise Exception()
    
        # Add all anime in the first page.
        for entry in jikan_res_json['anime']:
            anime.append(entry)
            Ayumi.debug("Added {} show {} to processing list.".format(listname, entry['title']))
        
        page = 2
        while (len(jikan_res_json['anime']) == 300):
            jikan_res = requests.get(listurl.format(user, str(page)))
            if jikan_res.status_code != 200 or 'anime' not in jikan_res:
                Ayumi.debug("Jikan returned a bad status code when attempting to get {}'s page {} {} list.".format(user, str(page), listname))
                raise Exception()
                
            try:
                jikan_res_json = jikan_res.json()
            except:
                jikan_res_json = dict()
            
            if 'anime' not in jikan_res_json:
                Ayumi.debug("Jikan.moe did not return an anime list on attempt to get {}'s page {} {} list.".format(user, str(page), listname))
                raise Exception()

            for entry in jikan_res_json['anime']:
                anime.append(entry)
                Ayumi.debug("Added {} page {} show {} to processing list.".format(listname, str(page), entry['title']))
            
            page += 1

        Ayumi.debug("Returning list with {} entires.".format(str(len(anime))))
        return anime
    
    except:
        # raise some kind of exception - somehow Jikan couldn't be reached
        Ayumi.debug("Akari encountered an unknown error when attempting to fetch {}'s {} list".format(user, listname))
        raise Exception()

def _fetch_retry(user, listurl, listname, times=5):
    """
    Jikan.moe is susceptible to randomly failing. This method allows us to try multiple times before really "failing"

    Params: See fetch_list()

    Returns: See fetch_list() if successful, or raises an Exception() otherwise
    """
    for i in range(times):
        try:
            Ayumi.debug("Attempt #{} to contact Jikan.moe for {}".format(i+1, listname))
            anime = _fetch_list(user, listurl, listname)
            Ayumi.debug("Attempt #{} succeeded".format(i+1))
            return anime
        except:
            # Sleep 5 seconds, and then try again
            Ayumi.debug("Attempt #{} failed, sleeping 5 seconds and trying again...".format(i+1))
            sleep(5)

    # If this point is reached, then there has been too many errors. Raise an exception
    Ayumi.debug("Akari was unable to contact Jikan.moe")
    raise Exception()

def akari_list(user, times=5):
    anime = list()
    try:
        jikan_res_watching = _fetch_retry(user, _JIKAN_USER_WATCHING, "Watching", times)
        jikan_res_ptw = _fetch_retry(user, _JIKAN_USER_PTW, "PTW", times)

        anime.extend(jikan_res_watching)
        anime.extend(jikan_res_ptw)
    except:
        # We couldn't find the user at all, so just return an empty list
        pass

    return anime

def is_user_watching_names(user, show_name, times=5):
    """
    Is a user watching this show or not?

    Params:
        user: username to lookup
        show_name: show name to match against

    Returns True if the show was found in the list, false if not
    """
    Ayumi.debug("Now finding if \"{}\" is in {}'s list".format(show_name, user))
    anime_list = akari_list(user, times)
    for show in anime_list:
        if show['title'] == show_name:
            Ayumi.info("\"{}\" was found in {}'s list".format(show_name, user), color=Ayumi.LGREEN)
            return True

    Ayumi.info("\"{}\" was not found in {}'s list".format(show_name, user), color=Ayumi.LYELLOW)
    return False

def is_user_watching_id(user, malID, times=5):
    """
    Is a user watching this show or not?

    Params:
        user: username to lookup
        malID: malID to match against
    """
    Ayumi.debug("Now finding if \"{}\" is in {}'s list".format(malID, user))
    anime_list = akari_list(user, times)
    for show in anime_list:
        if str(show['mal_id']) == str(malID):
            Ayumi.info("\"{}\" was found in {}'s list".format(malID, user), color=Ayumi.LGREEN)
            return True

    Ayumi.info("\"{}\" was not found in {}'s list".format(malID, user), color=Ayumi.LYELLOW)
    return False
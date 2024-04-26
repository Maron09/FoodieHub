# this is a helper function that displays the nearby restaurants around the user even if the lat and lng are not in the url it gets the lat&lng from the session if it exists and if it doesn't when it is in the url it saves it to the session
def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    elif 'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    else:
        return None
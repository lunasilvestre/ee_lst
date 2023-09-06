import ee

def add_band(image):
    """
    Add total precipitable water values and index for the LUT of SMW algorithm coefficients to the image.

    Parameters:
    - image (ee.Image): Image for which to interpolate the TPW data. Needs the 'system:time_start' image property.

    Returns:
    - ee.Image: Image with added 'TPW' and 'TPWpos' bands.
    """

    date = ee.Date(image.get('system:time_start'))
    year = date.get('year')
    month = date.get('month')
    day = date.get('day')
    # date1 = ee.Date.from_ymd(year, month, day)
    # date1 = ee.Date(f"{year}-{month}-{day}")
    dateString = year.format().cat('-').cat(month.format()).cat('-').cat(day.format())
    date1 = ee.Date(dateString)  
    date2 = date1.advance(1, 'days')

    def datedist(img):
        # return img.set('DateDist', abs(img.get('system:time_start') - date.millis()))
        return img.set('DateDist', ee.Number(img.get('system:time_start')).subtract(date.millis()).abs())


    TPWcollection = (ee.ImageCollection('NCEP_RE/surface_wv')
                     .filterDate(date1.format('yyyy-MM-dd'), date2.format('yyyy-MM-dd'))
                     .map(datedist))

    closest = TPWcollection.sort('DateDist').toList(2)

    # tpw1 = closest.get(0).select('pr_wtr') if closest.size() else ee.Image.constant(-999.0)
    tpw1 = ee.Image(closest.get(0)).select('pr_wtr') if closest.size() else ee.Image.constant(-999.0)
    # tpw2 = closest.get(1).select('pr_wtr') if closest.size() > 1 else tpw1
    # tpw2 = ee.Image(closest.get(1)).select('pr_wtr') if closest.size() > 1 else tpw1
    tpw2 = ee.Image(closest.get(1)).select('pr_wtr') if ee.Number(closest.size()).gt(1) else tpw1
    
    # time1 = tpw1.get('DateDist') / 21600000 if closest.size() else 1.0
    time1 = ee.Number(tpw1.get('DateDist')).divide(21600000) if ee.Number(closest.size()).gt(0) else ee.Number(1.0)
    # time2 = tpw2.get('DateDist') / 21600000 if closest.size() > 1 else 0.0
    time2 = ee.Number(tpw2.get('DateDist')).divide(21600000) if ee.Number(closest.size()).gt(1) else ee.Number(0.0)

    tpw = tpw1.expression('tpw1*time2+tpw2*time1', {
        'tpw1': tpw1,
        'time1': time1,
        'tpw2': tpw2,
        'time2': time2
    }).clip(image.geometry())

    pos = tpw.expression(
        "value = (TPW>0 && TPW<=6) ? 0" +
        ": (TPW>6 && TPW<=12) ? 1" +
        ": (TPW>12 && TPW<=18) ? 2" +
        ": (TPW>18 && TPW<=24) ? 3" +
        ": (TPW>24 && TPW<=30) ? 4" +
        ": (TPW>30 && TPW<=36) ? 5" +
        ": (TPW>36 && TPW<=42) ? 6" +
        ": (TPW>42 && TPW<=48) ? 7" +
        ": (TPW>48 && TPW<=54) ? 8" +
        ": (TPW>54) ? 9" +
        ": 0", {'TPW': tpw}).clip(image.geometry())

    withTPW = image.addBands(tpw.rename('TPW')).addBands(pos.rename('TPWpos'))

    return withTPW

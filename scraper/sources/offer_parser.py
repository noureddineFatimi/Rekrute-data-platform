def get_property(beautifulSoupHtml, selector, multiple=False):
    if multiple:
        selections = beautifulSoupHtml.select(selector)
        if selections:
            elements = [
                selection.get_text(separator="-", strip=True)
                for selection in selections
            ]
            element = " - ".join(elements)
        else:
            element = "not_defined"
    else:
        selection = beautifulSoupHtml.select_one(selector)
        element=selection.get_text(separator="-", strip=True) if selection else "not_defined"
    return element

def get_job_description(beautifulSoupHtml, h2Keys):
    sections = []
    for div in beautifulSoupHtml.find_all("div"):
        h2 = div.find("h2", recursive=False)
        if h2:
            titre = h2.get_text(" ", strip=True)
            if titre in h2Keys:
                contenu = div.get_text(
                    separator=" ",
                    strip=True
                )
                sections.append(contenu)
    return "\n".join(sections) if sections else "not_defined"

def create_new_offer(beautifulSoupHtml, link):
    titre=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail .row h1")
    sector=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail .row h2")
    experience=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail .row ul.featureInfo li[title='Expérience requise']")
    region=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail ul.featureInfo li[title='Région']")
    formation=get_property(beautifulSoupHtml=beautifulSoupHtml, selector='div.listWrpService.jobdetail ul.featureInfo li[title="Niveau d\'étude et formation"]')
    competencesPersonnelles=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail span.tagSkills", multiple=True)
    contrat=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail span[title='Type de contrat']")
    teletravail=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail span[title='Télétravail']")
    dateLimite=get_property(beautifulSoupHtml=beautifulSoupHtml, selector="div.listWrpService.jobdetail span.newjob b")
    description=get_job_description(beautifulSoupHtml=beautifulSoupHtml, h2Keys=["Poste :", "Profil recherché :"])

    offer={
        "titre": titre,
        "link": link,
        "sector": sector,
        "experience": experience,
        "region": region,
        "formation": formation,
        "competencesPersonnelles": competencesPersonnelles,
        "contrat": contrat,
        "teletravail": teletravail,
        "description": description,
        "dateLimite": dateLimite
    }

    return offer
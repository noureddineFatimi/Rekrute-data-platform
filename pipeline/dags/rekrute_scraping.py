from airflow.sdk import Param, dag, get_current_context, task


@dag(
    dag_id="rekrute_scraping",
    schedule=None,
    catchup=False,
    params={
        "url": Param("https://www.rekrute.com/offres.html", type="string"),
        "max_items": Param(1, type="integer", minimum=1),
    },
)
def rekrute_scraping():
    @task
    def run_scrap():
        from services.scraping_service import scrape_offers

        params = get_current_context()["params"]
        search_id = scrape_offers(url=params["url"], max_items=params["max_items"])
        return search_id

    @task
    def run_validate(search_id: int):
        from services.validating_loading_service import validate_and_load_offers

        result = validate_and_load_offers(search_id)
        return result

    search_id = run_scrap()
    run_validate(search_id)

rekrute_scraping()

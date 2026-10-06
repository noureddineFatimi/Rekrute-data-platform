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
    def get_proxies():
        from services.proxy_service import fetch_and_store_proxies
    
        dag_run_id = get_current_context()['run_id']
        fetch_and_store_proxies(dag_run_id=dag_run_id)
        return dag_run_id

    @task
    def run_scrap(dag_run_id: str):
        from services.scraping_service import scrape_offers

        params = get_current_context()["params"]
        search_id = scrape_offers(dag_run_id=dag_run_id, url=params["url"], max_items=params["max_items"])
        return search_id

    @task
    def run_validate(search_id: int):
        from services.validating_loading_service import validate_and_load_offers

        result = validate_and_load_offers(search_id)
        return result

    dag_run_id=get_proxies()
    search_id = run_scrap(dag_run_id)
    run_validate(search_id)

rekrute_scraping()

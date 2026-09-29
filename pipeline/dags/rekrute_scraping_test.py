from airflow.sdk import Param, dag, get_current_context, task


@dag(
    dag_id="rekrute_scraping_test",
    schedule=None,
    catchup=False,
    params={
        "url": Param("https://www.rekrute.com/offres.html", type="string"),
        "max_items": Param(1, type="integer", minimum=1),
    },
)
def rekrute_scraping_test():
    @task
    def run_scrap_job():
        from services.scraping_service import run_scraping_jobs

        params = get_current_context()["params"]
        return run_scraping_jobs(
            url=params["url"],
            max_items=params["max_items"],
        )

    run_scrap_job()


rekrute_scraping_test()

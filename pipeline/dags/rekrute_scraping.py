import logging
from datetime import timedelta
from airflow.sdk import Param, dag, get_current_context, task
# Nouveaux imports spécifiques à Airflow 3.0
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk.exceptions import AirflowFailException, AirflowSkipException

@dag(
    dag_id="rekrute_scraping",
    schedule=None,
    catchup=False,
    params={
        "url": Param("https://www.rekrute.com/offres.html", type="string"),
        "max_items": Param(1, type="integer", minimum=1),
        "proxy_retry_count": Param(0, type="integer"), 
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
        try:
            search_id = scrape_offers(dag_run_id=dag_run_id, url=params["url"], max_items=params["max_items"])
            return search_id
        except Exception as e:
            if "All proxies failed" in str(e):
                logging.error("Échec des proxies détecté. Forçage de l'échec de la tâche.")
                # Utilisation de la nouvelle exception du SDK Airflow 3
                raise AirflowFailException("All proxies failed") 
            raise e 

    @task(retries=3, retry_delay=timedelta(minutes=1))
    def run_validate(search_id: int):
        from services.validating_loading_service import validate_and_load_offers
        result = validate_and_load_offers(search_id)
        return result

    # --- NOUVELLE LOGIQUE DE RELANCE AIRFLOW 3 ---

    # Cette tâche ne s'exécutera QUE SI la tâche précédente échoue
    @task(trigger_rule="one_failed")
    def prepare_retry_conf():
        context = get_current_context()
        params = context["params"].copy()
        current_retry_count = params.get("proxy_retry_count", 0)
        
        if current_retry_count >= 3:
            logging.error("Limite de relances atteinte (3). Abandon.")
            # Si on skip cette tâche, la tâche suivante (Trigger) sera skippée aussi
            raise AirflowSkipException("Limite de relance atteinte")
            
        params["proxy_retry_count"] = current_retry_count + 1
        return params

    # --- DÉFINITION DU WORKFLOW ---
    
    dag_run_id = get_proxies()
    search_id = run_scrap(dag_run_id)
    
    # 1. Flux principal : La validation s'exécute si le scraping réussit
    run_validate(search_id)
    
    # 2. Flux d'erreur : Si search_id échoue, prepare_retry_conf s'active
    new_conf = prepare_retry_conf()
    search_id >> new_conf
    
    # L'opérateur classique accepte "new_conf" (qui est un XComArg dynamique)
    trigger_retry = TriggerDagRunOperator(
        task_id="trigger_retry_on_failure",
        trigger_dag_id="rekrute_scraping",
        conf=new_conf,
    )

rekrute_scraping()
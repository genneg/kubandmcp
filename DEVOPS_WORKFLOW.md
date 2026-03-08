# The DevOps Workflow: Da Locale a Produzione

Questo documento illustra il ciclo di vita completo del software in un'architettura Cloud Native, indicando esattamente i comandi da eseguire in ogni fase.

## 1. Sviluppo Locale (Python)
**Fase:** Scrittura e test del codice sorgente sul tuo PC.

*   `main.py`, `agent.py`: Il tuo codice applicativo.
*   `requirements.txt`: Elenco delle librerie Python necessarie.
*   `.env`: (NON COMMITTARE!) I tuoi segreti locali e credenziali API.

**Comandi:**
*   `python -m venv venv`: Crea l'ambiente virtuale.
*   `.\venv\Scripts\activate`: Attiva l'ambiente virtuale (su Windows).
*   `pip install -r requirements.txt`: Installa le dipendenze.
*   `python main.py`: Esegue l'applicazione in locale per testarla.

---

## 2. Containerizzazione (Docker)
**Fase:** Impacchettare il software e le sue dipendenze in un formato universale (Immagine) per farlo girare in modo identico ovunque (Container).

*   `Dockerfile`: "La Ricetta". Le istruzioni su come costruire l'Immagine Docker (es. parti da Linux, copia i file, installa requirements.txt, esegui python).

**Comandi Locali:**
*   `docker build -t mio-nome-app:latest .`: Cucina l'immagine leggendo il Dockerfile.
*   `docker run --rm -it mio-nome-app:latest`: Testa il container localmente (prima di Kubernetes).

---

## 3. Gestione del Codice Sensitivo e Versionamento (Git & GitHub)
**Fase:** Salvare snapshot (commit) del tuo lavoro e condividerlo in cloud.

*   `.gitignore`: Elenco di file e cartelle (come `.env` o `venv/`) che Git deve ignorare per evitare di pubblicarli su internet.

**Comandi:**
*   `git status`: Guarda cosa è cambiato.
*   `git add .`: Aggiungi tutte le modifiche "sullo stage".
*   `git commit -m "Messaggio"`: Salva il pacchetto di modifiche con un messaggio descrittivo.
*   `git push origin main`: Invia il codice pubblico su GitHub.

---

## 4. Automazione CI/CD: Continuous Integration (GitHub Actions)
**Fase:** Far sì che un robot cloud testi e compili per te ogni volta che fai "push".

*   `.github/workflows/ci.yaml`: Il file di configurazione per il robot (GitHub). Gli dici: *quando ricevi un push, installa python, testa le librerie, fai login a Docker Hub, costruisci l'immagine (docker build) e inviala (docker push)*.

**Mappa Mentale:** In questa fase, tu fai solo `git push`. Tutto il resto avviene da solo nel cloud. L'immagine Docker finisce nel **Container Registry** (es. Docker Hub) e riceve un tag (es. `kubandmcp:latest` o `kubandmcp:v1.2.3`).

---

## 5. Deployment Infrastruttura (Kubernetes / K8s)
**Fase:** Orchestare i Container. Decidere quanti ne vuoi `(ReplicaSet)`, come farli comunicare `(Service)`, dove gireranno. In locale, usi il tool `kind`.

*   `k8s/deployment.yaml`: Definisce il *cosa* e il *quanto* (es. "Voglio 2 repliche del Container `kubandmcp:latest`").
*   `k8s/service.yaml`: La rete. Apre le "porte" per far parlare i pod tra loro o col mondo esterno (LoadBalancer, ClusterIP, NodePort).

**Comandi K8s (Locali / Manuali):**
*   `kubectl apply -f ./k8s`: Invia i file YAML al cluster affinché li applichi (creando Pod, Deployment, Service ecc.).
*   `kubectl get pods`: Controlla lo stato dei tuoi container.
*   `kubectl logs <nome-pod>`: Leggi l'output o gli errori di un container.
*   `kubectl describe pod <nome-pod>`: Informazioni dettagliate se un pod fallisce (CrashLoopBackOff, ImagePullBackOff).
*   `kubectl delete -f ./k8s`: Elimina tutto ciò che è stato creato dai manifest in quella cartella.

**Per il testing su cluster Kind locale (senza GitHub Actions):**
*   `kind load docker-image kubandmcp:latest`: Trasferisci l'immagine dal tuo Docker locale ai nodi interni del cluster Kind.

---

## 6. Automazione CD: Continuous Deployment (GitOps con ArgoCD)
**Fase:** Non usi più `kubectl apply` in manuale. Cedi il comando del cluster ad ArgoCD. ArgoCD garantisce che lo *Stato Desiderato* (scritto nei file .yaml su GitHub) corrisponda perfettamente allo *Stato Reale* (i pod attivi nel cluster).

**Come funziona:**
1.  Un robot (ArgoCD) gira dentro il tuo cluster Kubernetes.
2.  Gli crei un **Application Manifest (ArgoCD YAML)** o glielo dici via UI: *"Il tuo unico scopo nella vita è osservare il mio repository GitHub 'kubandmcp', dentro la cartella 'k8s/'. Se vedi che cambia qualcosa, aggiorna i Pod per farli uguali a quei YAML"*.

**Il Flusso Finale "Mani in Tasca":**
1.  Scrivi codice in `main.py`.
2.  Fai `git commit` e `git push`.
3.  **GitHub Actions** scatta in automatico, builda l'immagine e la carica su Docker Hub.
4.  Tu aggiorni (se necessario) la versione dell'immagine su `k8s/deployment.yaml` e fai un altro `git push`.
5.  **ArgoCD** nota la modifica YAML, si accorge che il cluster è "OutOfSync", scarica da Docker Hub la nuova immagine e spegne/accende i Pod in modo controllato (Rolling Update). Tu non esegui nemmeno un comando Kubernetes.

---

### Diagnostica Rapida: Dove sono bloccato?

*   **Il codice crasha o dà eccezioni Python?** -> *Fase 1 (Locale)*: Sei nella cartella giusta? Hai attivato il venv? L'API key c'è?
*   **Errore `docker build` (pip install error, file not found)?** -> *Fase 2 (Dockerfile)*: Controlla i percorsi dei COPY nel Dockerfile.
*   **Errore in GitHub Actions? (Croce rossa su GitHub)** -> *Fase 4 (CI)*: Controlla i log nel tab "Actions" di GitHub. I segreti sono giusti? 
*   **Il Pod su K8s è in errore `ImagePullBackOff`?** -> *Fase 5 (K8s)*: Kubernetes non trova l'immagine. Non hai fatto `docker push` (o la action ha fallito), hai sbagliato il nome/tag in `deployment.yaml`, o in locale (su Kind) ti sei dimenticato di fare `kind load`.
*   **Il Pod su K8s è in errore `CrashLoopBackOff`?** -> *Fase 5 (K8s)*: L'immagine c'è, il container parte ma poi esplode subito. Controlla: `kubectl logs <nome-pod> --previous`. Probabilmente manca una variabile d'ambiente (`.env` in K8s si passa tramite Secret/ConfigMap) o il file Python cerca file su disco inesistenti.

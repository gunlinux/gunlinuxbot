package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/websocket"

	"ws_service/rqueue"
)

var ctx = context.Background()

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

func reader(conn *websocket.Conn) {
	for {
		// read in a message
		messageType, p, err := conn.ReadMessage()
		if err != nil {
			log.Println(err)
			return
		}
		// print out that message for clarity
		log.Println(string(p))
		if err := conn.WriteMessage(messageType, p); err != nil {
			log.Println(err)
			return
		}
	}
}

func homePage(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "HOME HTTP")
}

func wsEndpoint(w http.ResponseWriter, r *http.Request) {
	// upgrade this connection to a WebSocket
	// connection
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
	}
	actions := []string{
		"{\"action\": \"go.py\", \"args\": [\"loki\", \"15\"]}",
		"{\"action\": \"test1.py\"}",
		"{\"action\": \"test2.py\"}",
		"{\"action\": \"test3.py\"}",
		"{\"action\": \"test4.py\"}",
	}
	once := 0
	log.Println("Client Connected")
	for {
		if once < 4 {
			time.Sleep(1 * time.Second)
			err = ws.WriteMessage(1, []byte(actions[once]))
			once += 1
			if err != nil {
				log.Println(err)
				return
			} else {
				time.Sleep(1 * time.Second)
			}
		} else {
			once = 0
		}
	}
	log.Println("Killed client cause why not")
	ws.Close()

	return

	// listen indefinitely for new messages coming
	// through on our WebSocket connection
	// reader(ws)
}

func setupRoutes() {
	http.HandleFunc("/", homePage)
	http.HandleFunc("/ws", wsEndpoint)
}

func main() {
	fmt.Println("hello here general Kenobi")
	setupRoutes()

	redis_queue := os.Getenv("REDIS_QUEUE")
	if redis_queue == "" {
		redis_queue = "obs_events"
	}
	redis_cli := rqueue.RedisCli()
	val, _ := redis_cli.LPop(ctx, redis_queue).Result()

	fmt.Println("got q", val)

	log.Fatal(http.ListenAndServe("127.0.0.1:8080", nil))
}

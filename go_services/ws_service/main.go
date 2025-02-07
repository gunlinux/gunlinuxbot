package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/websocket"
  "github.com/redis/go-redis/v9"
  "github.com/joho/godotenv"

	"ws_service/rqueue"
)

var ctx = context.Background()
var redis_cli *redis.Client
var redis_queue string


func init() {
    // loads values from .env into the system
    if err := godotenv.Load(); err != nil {
        log.Print("No .env file found")
    }
		redis_queue = os.Getenv("REDIS_QUEUE")
		if redis_queue == "" {
			redis_queue = "obs_events"
		}
		redis_cli = rqueue.RedisCli()
}


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

	log.Println("Client Connected")
	for {
		val, err := redis_cli.LPop(ctx, redis_queue).Result()
		if err != nil {
			continue
		}

		time.Sleep(1 * time.Second)
		err = ws.WriteMessage(1, []byte(val))
		if err == nil {
			log.Println("Client ne ale")
			return
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



	host := os.Getenv("WS_SERVICE_HOST")
	if host == "" {
		fmt.Println("cant get host from evn")
		host = "127.0.0.1:8080"
	}

	log.Fatal(http.ListenAndServe(host, nil))
}

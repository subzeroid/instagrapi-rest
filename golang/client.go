package main

import (
	"io/ioutil"
	"log"
	"os"

	"github.com/go-resty/resty/v2"
)

const BaseUrl = "http://localhost:8000"

var client *resty.Client

func init() {
	client = resty.New()
	client.SetHostURL(BaseUrl)
	client.SetContentLength(true)
}

func getVersion() string {
	resp, err := client.R().Get("/version")
	if err != nil {
		log.Println(err)
	}
	return resp.String()
}

func pkFromCode(code string) string {
	resp, err := client.R().
		SetQueryParams(map[string]string{
			"code": code,
		}).
		Get("/media/pk_from_code")
	if err != nil {
		log.Println(err)
	}
	return resp.String()
}

func login(username string, password string, settings string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"username": username,
			"password": password,
			"settings": settings,
		}).Post("/auth/login")
	if err != nil {
		log.Println(err)
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
		return ""
	}
	return resp.String()
}

func relogin(sessionid string) {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid": sessionid,
		}).Post("/auth/relogin")
	if err != nil {
		log.Println(err)
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
	}
}

func photo_download(sessionid, url, folder string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid":  sessionid,
			"url":        url,
			"folder":     folder,
			"returnFile": "false",
		}).Post("/photo/download/by_url")
	if err != nil {
		log.Println(err)
		return ""
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
		return ""
	}
	return resp.String()
}

func getSettings(sessionid string) string {
	resp, err := client.R().
		SetQueryParams(map[string]string{
			"sessionid": sessionid,
		}).Get("/auth/settings")
	if err != nil {
		log.Println(err)
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
		return "{}"
	}
	return resp.String()
}

func loadSettings(file string) string {
	if _, err := os.Stat(file); err != nil {
		if os.IsNotExist(err) {
			return ""
		}
	}
	content, err := ioutil.ReadFile(file)
	if err != nil {
		log.Println(err)
		return "{}"
	}
	return string(content)
}

func saveSettings(file string, settings string) {
	fd, err := os.Create(file)
	defer fd.Close()
	_, err = fd.WriteString(settings)
	if err != nil {
		log.Println(err)
	}
}

func main() {
	log.Println("Version: ", getVersion())
	log.Println("pkFromCode: B1LbfVPlwIA -> ", pkFromCode("B1LbfVPlwIA"))
	settings := loadSettings("./settings.json")
	sessionid := login("adw0rd", "test", settings)
	if sessionid != "" {
		log.Println("SESSIONID: ", sessionid)
		settings = getSettings(sessionid)
		if settings != "{}" {
			log.Println(settings)
			saveSettings("./settings.json", settings)
		}
	} else {
		log.Fatal("Login error!")
	}
	// relogin(sessionid)
	log.Println("photo_download:", photo_download(sessionid, "https://www.instagram.com/p/COQebHWhRUg/", ""))
}

package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"

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

func pkFromUrl(url string) string {
	resp, err := client.R().
		SetQueryParams(map[string]string{
			"url": url,
		}).
		Get("/media/pk_from_url")
	if err != nil {
		log.Println(err)
	}
	return resp.String()
}

func id_from_username(sessionid, username string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid": sessionid,
			"username":  username,
		}).Post("/user/id_from_username")
	if err != nil {
		log.Println(err)
	}
	return resp.String()
}

func login(username, password string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"username": username,
			"password": password,
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

func photo_download(sessionid, media_pk, folder string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid":  sessionid,
			"media_pk":   media_pk,
			"folder":     folder,
			"returnFile": "false",
		}).Post("/photo/download")
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

func video_download(sessionid, media_pk, folder string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid":  sessionid,
			"media_pk":   media_pk,
			"folder":     folder,
			"returnFile": "false",
		}).Post("/video/download")
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
		}).Get("/auth/settings/get")
	if err != nil {
		log.Println(err)
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
		return "{}"
	}
	return resp.String()
}

func setSettings(sessionid, settings string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid": sessionid,
			"settings":  settings,
		}).Post("/auth/settings/set")
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
			return "{}"
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

func user_stories(sessionid, id string, amount int) []string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid": sessionid,
			"user_id":   id,
			"amount":    strconv.Itoa(amount),
		}).Post("/story/user_stories")
	if err != nil {
		log.Println(err)
		return []string{}
	}
	if resp.StatusCode() != 200 {
		log.Println(resp.String())
		return []string{}
	}

	log.Println(resp.String())

	var (
		stories []map[string]interface{}
		result  []string
	)

	json.Unmarshal([]byte(resp.String()), &stories)
	for _, v := range stories {
		result = append(result, strings.SplitN(v["id"].(string), "_", 2)[0])
	}
	return result
}

func igtv_download(sessionid, media_pk, folder string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid":  sessionid,
			"media_pk":   media_pk,
			"folder":     folder,
			"returnFile": "false",
		}).Post("/igtv/download")
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

func story_download(sessionid, story_pk, folder string) string {
	resp, err := client.R().
		SetFormData(map[string]string{
			"sessionid":  sessionid,
			"story_pk":   story_pk,
			"folder":     folder,
			"returnFile": "false",
		}).Post("/story/download")
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

func album_upload(sessionid string, files []string, caption string) string {
	r := client.R()
	for _, path := range files {
		path = strings.Trim(path, "\" ")
		filedata, _ := ioutil.ReadFile(path)
		r = r.SetFileReader("files", filepath.Base(path), bytes.NewReader(filedata))
	}

	resp, err := r.SetFormData(map[string]string{
		"sessionid": sessionid,
		"caption":   caption,
	}).Post("/album/upload")

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

func photo_upload_to_story(sessionid, filephoto string) string {
	resp, err := client.R().
		SetFile("file", strings.Trim(filephoto, "\" ")).
		SetFormData(map[string]string{
			"sessionid": sessionid,
		}).Post("/photo/upload_to_story")

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

func main() {
	log.Println("Version: ", getVersion())
	log.Println("pkFromCode: B1LbfVPlwIA -> ", pkFromCode("B1LbfVPlwIA"))
	settings := loadSettings("./settings.json")
	sessionid := ""
	if settings != "{}" {
		sessionid = setSettings("", settings)
	} else {
		sessionid = login("example", "test")
	}
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

	photo := photo_download(sessionid, pkFromUrl("https://www.instagram.com/p/COQebHWhRUg/"), "")
	log.Println("photo_download:", photo)

	photo_story := photo_upload_to_story(sessionid, photo)
	log.Println("photo_upload_to_story:", photo_story)

	video := video_download(sessionid, pkFromUrl("https://www.instagram.com/p/CGgDsi7JQdS/"), "")
	log.Println("video_download:", video)

	igtv := igtv_download(sessionid, pkFromUrl("https://www.instagram.com/p/CRHO6N6HLvQ/"), "")
	log.Println("igtv_download:", igtv)

	stories := user_stories(sessionid, id_from_username(sessionid, "therock"), 1)
	log.Println(stories)

	if len(stories) > 0 {
		story := story_download(sessionid, stories[0], "")
		log.Println("story_download:", story)
	}

	result := album_upload(sessionid, []string{photo, video}, "hello world")
	log.Println(result)

}

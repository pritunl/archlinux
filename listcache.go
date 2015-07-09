package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const body = `<html>
<head><title>Index of %s</title></head>
<body bgcolor="white">
<h1>Index of %s</h1><hr><pre><a href="../">../</a>
%s
</pre><hr></body>
</html>
`

type Item struct {
	Name      string
	IsDir     bool
	Formatted string
}

type Items struct {
	items []Item
}

func (s *Items) Len() (n int) {
	n = len(s.items)
	return
}

func (s *Items) Less(i int, j int) bool {
	if s.items[i].IsDir && !s.items[j].IsDir {
		return true
	}
	if s.items[i].Name[:1] == "." && s.items[i].Name[:1] != "." {
		return true
	}
	return s.items[i].Name < s.items[j].Name
}

func (s *Items) Swap(i int, j int) {
	s.items[i], s.items[j] = s.items[j], s.items[i]
}

func (s *Items) Add(item Item) {
	s.items = append(s.items, item)
}

func (s *Items) Sort() {
	sort.Sort(s)
}

func (s *Items) Join(sep string) (data string) {
	for i, item := range s.items {
		if i != 0 {
			data += sep
		}
		data += item.Formatted
	}
	return
}

func main() {
	path := filepath.Clean(os.Args[1])
	pathFrm := strings.Replace(path, "/mirror", "", 1) + "/"
	if pathFrm[:1] != "/" {
		pathFrm = "/" + pathFrm
	}

	items := &Items{}

	itemsAll, err := ioutil.ReadDir(path)
	if err != nil {
		panic(err)
	}

	for _, item := range itemsAll {
		name := item.Name()
		if name == "index.html" {
			continue
		}

		modTime := item.ModTime().Format("02-Jan-2006 15:04")

		if item.Mode()&os.ModeSymlink != 0 {
			linkPath, err := os.Readlink(filepath.Join(path, item.Name()))
			if err != nil {
				panic(err)
			}

			itm, err := os.Lstat(linkPath)
			if err != nil {
				if os.IsNotExist(err) {
					continue
				}
				panic(err)
			}
			item = itm
		}

		size := ""
		if item.IsDir() {
			name += "/"
			size = "-"
		} else {
			size = fmt.Sprintf("%d", item.Size())
		}

		formattedName := name
		if len(formattedName) > 50 {
			formattedName = formattedName[:47] + "..>"
		}

		items.Add(Item{
			Name:  name,
			IsDir: item.IsDir(),
			Formatted: fmt.Sprintf(
				`<a href="%s">`, name) + fmt.Sprintf(
				"%-54s %s % 19s", formattedName+"</a>", modTime, size),
		})
	}

	items.Sort()

	fmt.Printf(body, pathFrm, pathFrm, items.Join("\n"))
}

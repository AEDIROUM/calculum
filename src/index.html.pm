#lang pollen
◊; vim: set spelllang=fr:

◊header[#:class "site-header"]{
    ◊h1{Calculum}
    ◊h2{Club d’algorithmique compétitive universitaire de l’Université de Montréal}
}

◊span[#:class "icon-before icon-calendar"]{
    Horaire:
    (TBD)
}
 · ◊span[#:class "icon-before icon-pin"]{
    Local:
    ◊out-link["https://www.iro.umontreal.ca/~robitail/3e-etage.html"]{AA-3192}
}

Le club se réunit chaque semaine autour de nouveaux ◊em{casse-têtes informatiques} qui feront appel à vos connaissances en algorithmique, en logique et en programmation.
Outre le plaisir à les résoudre, ces casse-têtes offrent un entraînement aux compétitions de programmation (◊out-link["https://icpc.global"]{ICPC}, ◊out-link["https://csgames.org"]{CS Games}, ◊out-link["https://facebook.com/codingcompetitions/hacker-cup"]{Hacker Cup}, ◊out-link["https://adventofcode.com"]{Advent of Code}, ◊out-link["https://en.wikipedia.org/wiki/Category:Programming_contests"]{…}) et aux questions posées en entrevue par certaines grandes compagnies.
Que vous soyez simple curieux, débutant ou déjà aguerri, soyez les bienvenus au Calculum!

Questions, commentaires, suggestions:◊br{}
◊span[#:class "code"]{calculum [at] iro.umontreal.ca}

◊div[#:class "box-highlight"]{
    ◊h2{👼 Etes-vous un nouveau ? 👼}
    ◊in-link["nouveau.html"]{Appuyez-ici!}
}

◊h2{
    Activités
    ◊span[#:class "feed-link icon-before icon-rss"]{◊in-link["feeds/posts.xml"]{Flux RSS}}
}

◊(define post-list (list-posts "posts.ptree"))
◊ol[#:class "post-list"]{
    ◊for/splice[[(post post-list)]]{
        ◊li{◊in-link[post]{
            ◊article[#:class (if (post-upcoming? post) "upcoming" "")]{
                ◊header{
                    ◊h3{
                        ◊span{◊post-title[post]}
                        ◊datetime[#:datetime (post-iso-date post)]{le ◊post-human-date[post]}
                    }
                    ◊post-summary[post]
                }
            }
        }}
    }
}

◊footer[#:class "site-footer"]{
    Généré à l’aide de ◊out-link["https://docs.racket-lang.org/pollen"]{Pollen}
     · ◊span[#:class "icon-before icon-git"]{◊out-link["https://github.com/AEDIROUM/calculum"]{Code source}}
}

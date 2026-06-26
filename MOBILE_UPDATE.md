# MOBILE_UPDATE.md — Adaptation responsive & accessibilité

**Projet :** SmartCards — Plateforme d'apprentissage (Flask)
**Contexte :** Titre professionnel RNCP « Développeur web et web mobile »
**Objectif :** Rendre l'interface existante entièrement responsive (mobile-first) et accessible (RGAA), **sans réécrire l'architecture**.

Toutes les règles CSS responsive ont été ajoutées **en complément** (`@media (max-width: 768px)` et `@media (max-width: 480px)`) et ne remplacent jamais les styles desktop.

---

## Récapitulatif des fichiers modifiés

| Fichier | Nature des changements |
|---|---|
| `Frontend/templates/components/header.html` | Accessibilité du bouton hamburger (aria-label FR, aria-expanded, aria-controls, icônes décoratives) |
| `Frontend/templates/components/sidebar.html` | Correction d'un bouton non fermé, aria-label sur la croix de fermeture, libellé de navigation |
| `Frontend/static/js/main.js` | Synchronisation de `aria-expanded` à l'ouverture/fermeture du menu |
| `Frontend/static/css/style.css` | Bloc responsive + accessibilité : focus clavier visible, cibles tactiles 44×44, mises en page mobiles, contraste du copyright |
| `Frontend/templates/session.html` | Upload PDF mobile (bouton « Choisir un fichier » visible), aria-labels, focus visible, cibles tactiles, responsive de la page |

---

## 1. Menu : hamburger / drawer accessible

> Note : la navigation utilisait déjà un **menu tiroir (drawer)** ouvert par un bouton hamburger, avec fermeture au clic sur l'overlay (clic en dehors) et touche `Échap`, ainsi qu'une animation `translateX`. Le travail a donc consisté à **fiabiliser l'accessibilité** de ce menu existant, pas à le recréer.

### `Frontend/templates/components/header.html`

**Avant :**
```html
<button class="burger-btn" id="burgerBtn" aria-label="Toggle Menu">
    <i data-lucide="menu" class="menu-icon"></i>
    <i data-lucide="x" class="close-icon hidden"></i>
</button>
```

**Après :**
```html
<button class="burger-btn" id="burgerBtn" aria-label="Ouvrir le menu de navigation" aria-expanded="false" aria-controls="menuSidebar">
    <i data-lucide="menu" class="menu-icon" aria-hidden="true"></i>
    <i data-lucide="x" class="close-icon hidden" aria-hidden="true"></i>
</button>
```
*Pourquoi : libellé en français, état d'ouverture annoncé aux lecteurs d'écran (`aria-expanded`), lien explicite vers le panneau contrôlé (`aria-controls`), icônes marquées décoratives.*

### `Frontend/templates/components/sidebar.html`

**Avant** (bouton « Dashboard » jamais fermé → boutons imbriqués, HTML invalide ; croix sans libellé) :
```html
<button class="menu-close-btn" id="menuCloseBtn">
    <i data-lucide="x"></i>
</button>
...
<nav class="menu-nav">
    <button class="menu-item ..." onclick="window.location.href='/dashboard'">
        <i data-lucide="trending-up"></i>
        Dashboard
    <button class="menu-item ..." onclick="window.location.href='/session'">
```

**Après** (balise fermée + libellés d'accessibilité) :
```html
<button class="menu-close-btn" id="menuCloseBtn" aria-label="Fermer le menu de navigation">
    <i data-lucide="x" aria-hidden="true"></i>
</button>
...
<nav class="menu-nav" aria-label="Navigation principale">
    <button class="menu-item ..." onclick="window.location.href='/dashboard'">
        <i data-lucide="trending-up" aria-hidden="true"></i>
        Dashboard
    </button>
    <button class="menu-item ..." onclick="window.location.href='/session'">
```

### `Frontend/static/js/main.js`

**Avant :**
```javascript
function openMenu() {
    menuOverlay.classList.add('active');
    menuSidebar.classList.add('active');
    ...
}
function closeMenu() {
    menuOverlay.classList.remove('active');
    menuSidebar.classList.remove('active');
    ...
}
```

**Après :**
```javascript
function openMenu() {
    menuOverlay.classList.add('active');
    menuSidebar.classList.add('active');
    burgerBtn.setAttribute('aria-expanded', 'true');
    ...
}
function closeMenu() {
    menuOverlay.classList.remove('active');
    menuSidebar.classList.remove('active');
    burgerBtn.setAttribute('aria-expanded', 'false');
    ...
}
```
*Pourquoi : l'état `aria-expanded` reflète l'ouverture réelle du drawer pour les technologies d'assistance.*

---

## 2. Mises en page responsive (dashboard / flashcards / quiz)

> Le `style.css` contenait déjà : `stats-grid → 1 colonne` (≤768px), `additional-stats → 2 puis 1 colonne`, et l'empilement des en-têtes flashcard/quiz. Les ajouts ci-dessous **complètent** ces règles.

### `Frontend/static/css/style.css` (bloc ajouté en fin de fichier)

**Ajout — Tablette / mobile (≤ 768px) :**
```css
@media (max-width: 768px) {
    .main-content { padding: 1.5rem 1rem; }

    /* Quiz : statut + bouton empilés, bouton pleine largeur */
    .quiz-controls { flex-direction: column; align-items: stretch; gap: 1rem; }
    .quiz-next-btn { width: 100%; justify-content: center; }
    .quiz-question-text { font-size: 1.25rem; line-height: 1.4; }

    /* Options de quiz : pleine largeur, texte non tronqué */
    .quiz-option {
        width: 100%;
        white-space: normal;
        word-break: break-word;
        text-align: left;
    }
}
```

**Ajout — Mobile (≤ 480px) :**
```css
@media (max-width: 480px) {
    .header-content { padding: 0.875rem 1rem; }

    /* Flashcard : ratio lisible, pas de débordement */
    .flashcard-wrapper { height: 360px; }
    .flashcard-front, .flashcard-back { padding: 1.5rem; }
    .flashcard-question { font-size: 1.4rem; line-height: 1.35; }
    .flashcard-answer { font-size: 1.05rem; line-height: 1.5; }

    /* Actions flashcard empilées et pleine largeur */
    .flashcard-actions { flex-direction: column; }
    .flashcard-action-btn { width: 100%; justify-content: center; }

    /* Stats : 2 colonnes au lieu de 3 pour la lisibilité */
    .flashcard-stats { grid-template-columns: repeat(2, 1fr); }

    .quiz-question-text { font-size: 1.15rem; }
    .quiz-score-value { font-size: 2.5rem; }
}
```
*Résultat : grille de stats → 1 colonne (déjà en place), flashcards à ratio lisible sans débordement, options de quiz en pleine largeur sans texte tronqué.*

---

## 3. Cibles tactiles minimum 44×44 px (WCAG 2.5.5 / RGAA)

### `Frontend/static/css/style.css`

**Ajout :**
```css
.burger-btn,
.menu-close-btn,
.menu-item,
.menu-logout,
.flashcard-action-btn,
.flashcard-nav-btn,
.quiz-option,
.quiz-next-btn,
.quiz-restart-btn,
.flashcard-end-btn,
.modal-btn {
    min-height: 44px;
    min-width: 44px;
}
```
*Couvre notamment les boutons « Compris ! » / « À revoir » et les options de quiz.*

### `Frontend/templates/session.html` (CSS interne — cette page n'inclut pas `style.css`)

**Ajout :**
```css
.back-btn   { min-height: 44px; min-width: 44px; }
.file-remove { min-height: 44px; min-width: 44px; }
.upload-browse-btn { min-height: 44px; /* ... */ }
```

---

## 4. Upload PDF utilisable sur mobile

### `Frontend/templates/session.html`

**Avant** (zone de drop seule ; le drag & drop est peu utilisable au doigt) :
```html
<div class="upload-title">Glissez votre PDF ici</div>
<div class="upload-subtitle">ou cliquez pour parcourir vos fichiers</div>
<span class="upload-hint">PDF uniquement · Max 20 Mo</span>
```

**Après** (bouton de sélection de fichier clairement visible) :
```html
<div class="upload-title">Glissez votre PDF ici</div>
<div class="upload-subtitle">ou utilisez le bouton ci-dessous</div>
<button type="button" class="upload-browse-btn"
        onclick="event.stopPropagation(); document.getElementById('pdfInput').click()"
        aria-label="Choisir un fichier PDF depuis votre appareil">
    <i data-lucide="folder-open" aria-hidden="true"></i>
    Choisir un fichier
</button>
<div><span class="upload-hint">PDF uniquement · Max 20 Mo</span></div>
```

**CSS du bouton (ajout, `session.html`) :**
```css
.upload-browse-btn {
    display: inline-flex; align-items: center; justify-content: center; gap: .5rem;
    margin-top: 1.25rem; min-height: 44px; padding: .75rem 1.5rem;
    border-radius: .75rem;
    background: linear-gradient(to right, var(--gradient-orange), var(--gradient-purple));
    color: #fff; font-size: .9rem; font-weight: 600; border: none; cursor: pointer;
    transition: transform .2s, box-shadow .2s;
}
```
*Le drag & drop existant est conservé ; le bouton offre une alternative tactile fiable. Sur ≤480px, le bouton passe en pleine largeur.*

**Responsive de la page (ajout) :**
```css
@media (max-width: 768px) {
    .page-wrapper { padding: 2rem 1rem 3rem; }
    .upload-zone  { padding: 2rem 1.25rem; }
}
@media (max-width: 480px) {
    .type-grid { grid-template-columns: 1fr; }
    .page-title { font-size: 1.75rem; }
    .page-subtitle br, .page-title br { display: none; }
    .upload-browse-btn { width: 100%; }
}
```

---

## 5. Accessibilité RGAA

### 5.1 Focus clavier visible (RGAA 10.7)

**`Frontend/static/css/style.css` (ajout) :**
```css
a:focus-visible,
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible,
.menu-item:focus-visible,
.quiz-option:focus-visible,
.flashcard:focus-visible {
    outline: 3px solid #ff8c5a;
    outline-offset: 2px;
    border-radius: 8px;
}
a:focus:not(:focus-visible),
button:focus:not(:focus-visible) { outline: none; }
```
*Même règle dupliquée dans `session.html` (page autonome sans `style.css`).*

### 5.2 Libellés des boutons icônes (RGAA 1.x / 4.x)

- `header.html` : `aria-label="Ouvrir le menu de navigation"` + `aria-expanded`.
- `sidebar.html` : `aria-label="Fermer le menu de navigation"` ; `<nav aria-label="Navigation principale">`.
- `session.html` : `aria-label` sur le bouton retour, le bouton « Choisir un fichier » et la suppression de fichier ; toutes les icônes décoratives marquées `aria-hidden="true"`.

### 5.3 Sélection du mode au clavier (RGAA 7.x — éléments interactifs)

Les cartes de choix du mode (`session.html`) étaient des `<div onclick>` non focusables et non actionnables au clavier.

**Avant :**
```html
<div class="type-card quiz" data-type="quiz" onclick="selectType('quiz')">
```

**Après :**
```html
<div class="type-card quiz" data-type="quiz" role="button" tabindex="0"
     aria-pressed="false" aria-label="Mode Quizz"
     onclick="selectType('quiz')" onkeydown="handleTypeKey(event, 'quiz')">
```

**JS associé :**
```javascript
function selectType(type) {
    document.querySelectorAll('.type-card').forEach(c => {
        c.classList.remove('selected');
        c.setAttribute('aria-pressed', 'false');
    });
    const card = document.querySelector(`.type-card.${type}`);
    card.classList.add('selected');
    card.setAttribute('aria-pressed', 'true');
    ...
}
function handleTypeKey(e, type) {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        selectType(type);
    }
}
```
*Les cartes sont désormais focusables (`tabindex="0"`), activables par `Entrée`/`Espace`, exposées comme boutons (`role="button"`) et leur état sélectionné est annoncé (`aria-pressed`).*

### 5.4 Contraste des couleurs sur fond sombre (RGAA 3.2)

**`Frontend/static/css/style.css` — `.footer-copyright`**

**Avant :**
```css
.footer-copyright { color: rgba(255, 255, 255, 0.4); /* ratio insuffisant */ }
```

**Après :**
```css
.footer-copyright { color: rgba(255, 255, 255, 0.62); /* contraste conforme */ }
```

---

## Principe de non-régression

- Aucune règle desktop existante n'a été supprimée ni remplacée.
- Tous les ajustements mobiles sont encapsulés dans `@media (max-width: 768px)` / `@media (max-width: 480px)`.
- `:focus-visible` n'affiche le contour qu'en navigation **clavier** : aucun impact visuel à la souris.
- Les `min-height/min-width: 44px` ne réduisent jamais les éléments existants (la plupart respectaient déjà cette taille).

## Points de vérification (recette)

1. < 768px : le menu s'ouvre/ferme via le hamburger, fermeture au clic extérieur et via `Échap`.
2. Dashboard : grille de statistiques sur une seule colonne.
3. Flashcards : carte lisible, boutons « Compris ! » / « À revoir » empilés et ≥ 44px.
4. Quiz : options en pleine largeur, texte complet (non tronqué), bouton « Suivant » pleine largeur.
5. Session : bouton « Choisir un fichier » visible et fonctionnel au doigt.
6. Tabulation clavier : contour de focus visible sur tous les éléments interactifs.

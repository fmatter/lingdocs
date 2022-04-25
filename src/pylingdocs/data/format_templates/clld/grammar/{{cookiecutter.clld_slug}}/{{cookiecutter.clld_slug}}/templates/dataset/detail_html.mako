<%inherit file="../home_comp.mako"/>

<%def name="sidebar()">
    <div class="well">
        <h3>Sidebar</h3>
        <p>
            {{cookiecutter.citation}}
        </p>
    </div>
</%def>

<h2>Welcome to {{cookiecutter.clld_slug}}</h2>

<p class="lead">
    {{cookiecutter.clld_slug}}
</p>
<p>
    More content.
</p>

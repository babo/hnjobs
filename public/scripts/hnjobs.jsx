var

DislikeButton = React.createClass({
    handleClick: function (tbd) {
        var url=this.props.url + '/update/' + this.props.id;

        $.ajax({
            url: url,
            type: tbd ? 'DELETE' : 'POST',
            success: function (data) {
                if (data.success === true) {
                    this.props.hide_cb(this.props.id);
                } else {
                    console.error('Failed to hide ' + this.props.id);
                }

            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return (
            <div className="row">
                <div className="col-md-1">
                    <button onClick={this.handleClick.bind(this, false)} type="button" className="btn btn-sn btn-success">Like</button>
                </div>
                <div className="col-md-1">
                    <button onClick={this.handleClick.bind(this, true)} type="button" className="btn btn-sn btn-warning">Hide</button>
                </div>
            </div>
        );
    }
}),

Comment = React.createClass({
    getInitialState: function () {
        return {liked: true};
    },
    hide_cb: function (job_id) {
        this.setState({liked: !this.state.liked});
    },
    render: function () {
        if (!this.state.liked) {
            return (<p></p>);
        } else {
            var rawMarkup = this.props.children.toString(),
                when = new Date( this.props.time * 1000),
                p = rawMarkup.indexOf('<p>'),
                title = p === -1 ? '' : rawMarkup.substring(0, p),
                body = p === -1 ? rawMarkup : rawMarkup.substring(p) + '</p>';
            return (
                <div className='comment list-group-item'>
                    <div className="row">
                        <div className="col-md-11">
                            {when.toLocaleString()}
                        </div>
                        <div className="col-md-1">
                            <span className="label label-info">
                                <a target="_blank" href={"https://news.ycombinator.com/user?id=" + this.props.author}>
                                    {this.props.author}
                                </a>
                            </span>
                        </div>
                    </div>

                    <h4 className="list-group-item-heading" dangerouslySetInnerHTML={{__html: title}}></h4>
                    <div className='list-group-item-text'>
                        <span dangerouslySetInnerHTML={{__html: body}} />
                        <DislikeButton id={this.props.id} url={this.props.url} hide_cb={this.hide_cb}/>
                    </div>
                </div>
            );
        }
    }
}),

CommentList = React.createClass({
    render: function () {
        var url = this.props.url,
            commentNodes = this.props.data.map(function (comment) {
            return (
                <Comment author={comment.by}  key={comment.id} id={comment.id} time={comment.time} url={url}>
                    {comment.text}
                </Comment>
            );
        });
        return (
            <div className='commentList list-group'>
                {commentNodes}
            </div>
        );
    }
}),

CommentBox = React.createClass({
    loadCommentsFromServer: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            data: {navmode: this.state.navmode, filter: this.state.searchFilter},
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return {data: [], navmode: 0, searchFilter: ""};
    },
    componentDidMount: function () {
        this.loadCommentsFromServer();
    },
    handleClick: function (which) {
        if (this.state.navmode !== which && which >= 0 && which < 4) {
            this.setState({navmode: which}, this.loadCommentsFromServer);
        }
    },
    handleSearch: function (e) {
        e.preventDefault();
        var newFilter = e.target.searchBox.value.trim();
        this.setState({searchFilter: newFilter}, this.loadCommentsFromServer);
    },
    render: function () {
        return (
            <div className='commentBox'>
                <div className="commentsNav navbar navbar-default" role="navigation">
                    <span className="navbar-text">
                        HN Jobs ({this.state.data.length})
                    </span>
                    <ul className="nav navbar-nav">
                        <li role="presentation" className={this.state.navmode === 0 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 0)}>Potential</a></li>
                        <li role="presentation" className={this.state.navmode === 1 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 1)}>Cool</a></li>
                        <li role="presentation" className={this.state.navmode === 2 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 2)}>Uncool</a></li>
                        <li role="presentation" className={this.state.navmode === 3 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 3)}>Remote</a></li>
                    </ul>
                    <form className="navbar-form navbar-right" role="search" onSubmit={this.handleSearch}>
                        <div className="form-group">
                            <input type="text" className="form-control" placeholder="Filter" name="searchBox" title="Filter jobs, regex supported" />
                        </div>
                        <button type="submit" className="btn btn-default" aria-label="Search">
                            <span className="glyphicon glyphicon-search" aria-hidden="true"></span>
                        </button>
                    </form>
                </div>

                <h1><a target="_blank" href={"https://news.ycombinator.com/item?id={this.props.id}"}>HN Jobs</a></h1>
                <CommentList data={this.state.data} url={this.props.url} />
            </div>
        );
    }
});

ReactDOM.render(
    <CommentBox url='/hnjobs' />,
    document.getElementById('content')
);

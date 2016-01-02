var

DislikeButton = React.createClass({
    handleCommentSubmit: function (comment) {
        var comments = this.state.data,
            newComments = comments.concat([comment]);
        this.setState({data: newComments});

    },
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
                title = p === -1 ? rawMarkup : rawMarkup.substring(0, p),
                body = p === -1 ? '' : rawMarkup.substring(p);
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
    loadCommentsFromServer: function (navmode) {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            data: {navmode: navmode},
            success: function (data) {
                this.setState({data: data, navmode: navmode});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return {data: [], navmode: 0};
    },
    componentDidMount: function () {
        this.loadCommentsFromServer(this.state.navmode);
    },
    handleClick: function (which) {
        if (this.state.navmode !== which && which >= 0 && which < 4) {
            this.loadCommentsFromServer(which);
        }
    },
    render: function () {
        return (
            <div className='commentBox'>
                <ul className="nav nav-tabs">
                    <li role="presentation" className={this.state.navmode === 0 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 0)}>Potential</a></li>
                    <li role="presentation" className={this.state.navmode === 1 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 1)}>Cool</a></li>
                    <li role="presentation" className={this.state.navmode === 2 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 2)}>Uncool</a></li>
                    <li role="presentation" className={this.state.navmode === 3 ? 'active' : ''}><a onClick={this.handleClick.bind(this, 3)}>Remote</a></li>
                </ul>

                <h1><a target="_blank" href={"https://news.ycombinator.com/item?id=9327840"}>HN Jobs</a></h1>
                <CommentList data={this.state.data} url={this.props.url} />
            </div>
        );
    }
});

React.render(
    <CommentBox url='/hnjobs' />,
    document.getElementById('content')
);
